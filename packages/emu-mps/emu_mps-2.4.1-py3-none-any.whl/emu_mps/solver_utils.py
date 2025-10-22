import torch
from typing import Callable, Sequence

from emu_base import krylov_exp
from emu_base.math.krylov_energy_min import krylov_energy_minimization
from emu_base.utils import deallocate_tensor
from emu_mps import MPS, MPO
from emu_mps.utils import split_tensor
from emu_mps.mps_config import MPSConfig


def make_op(
    time_step: float | complex,
    state_factors: Sequence[torch.Tensor],
    baths: tuple[torch.Tensor, torch.Tensor],
    ham_factors: Sequence[torch.Tensor],
) -> tuple[torch.Tensor, torch.device, Callable[[torch.Tensor], torch.Tensor]]:
    assert len(state_factors) == 2
    assert len(baths) == 2
    assert len(ham_factors) == 2

    left_state_factor, right_state_factor = state_factors
    left_bath, right_bath = baths
    left_ham_factor, right_ham_factor = ham_factors

    left_device = left_state_factor.device
    right_device = right_state_factor.device

    left_bond_dim = left_state_factor.shape[0]
    right_bond_dim = right_state_factor.shape[-1]

    # Computation is done on left_device (arbitrary)

    right_state_factor = right_state_factor.to(left_device)

    combined_state_factors = torch.tensordot(
        left_state_factor, right_state_factor, dims=1
    ).reshape(left_bond_dim, 4, right_bond_dim)

    deallocate_tensor(left_state_factor)
    deallocate_tensor(right_state_factor)

    left_ham_factor = left_ham_factor.to(left_device)
    right_ham_factor = right_ham_factor.to(left_device)
    right_bath = right_bath.to(left_device)

    combined_hamiltonian_factors = (
        torch.tensordot(left_ham_factor, right_ham_factor, dims=1)
        .transpose(2, 3)
        .contiguous()
        .view(left_ham_factor.shape[0], 4, 4, -1)
    )

    def op(x: torch.Tensor) -> torch.Tensor:
        return time_step * apply_effective_Hamiltonian(
            x, combined_hamiltonian_factors, left_bath, right_bath
        )

    return combined_state_factors, right_device, op


def new_right_bath(
    bath: torch.Tensor, state: torch.Tensor, op: torch.Tensor
) -> torch.Tensor:
    bath = torch.tensordot(state, bath, ([2], [2]))
    bath = torch.tensordot(op.to(bath.device), bath, ([2, 3], [1, 3]))
    bath = torch.tensordot(state.conj(), bath, ([1, 2], [1, 3]))
    return bath


"""
function to compute the right baths. The three indices in the bath are as follows:
(bond of state conj, bond of operator, bond of state)
The baths have shape
-xx
-xx
-xx
with the index ordering (top, middle, bottom)
bath tensors are put on the device of the factor to the left
"""


def right_baths(state: MPS, op: MPO, final_qubit: int) -> list[torch.Tensor]:
    state_factor = state.factors[-1]
    bath = torch.ones(1, 1, 1, device=state_factor.device, dtype=state_factor.dtype)
    baths = [bath]
    for i in range(len(state.factors) - 1, final_qubit - 1, -1):
        bath = new_right_bath(bath, state.factors[i], op.factors[i])
        bath = bath.to(state.factors[i - 1].device)
        baths.append(bath)
    return baths


"""
Computes H(psi) where
    x-    -x
    x  ||  x             ||
H = x- xx -x  and psi = -xx-
    x  ||  x
    x-    -x

Expects the two qubit factors of the MPS precontracted,
with one 'fat' physical index of dim 4 and index ordering
(left bond, physical index, right bond):
         ||
      -xxxxxx-
The Hamiltonian should have an index ordering of
(left bond, out, in, right bond).
The baths must have shape (top, middle, bottom).
All tensors must be on the same device
"""


def apply_effective_Hamiltonian(
    state: torch.Tensor,
    ham: torch.Tensor,
    left_bath: torch.Tensor,
    right_bath: torch.Tensor,
) -> torch.Tensor:
    assert left_bath.ndim == 3 and left_bath.shape[0] == left_bath.shape[2]
    assert right_bath.ndim == 3 and right_bath.shape[0] == right_bath.shape[2]
    assert left_bath.shape[2] == state.shape[0] and right_bath.shape[2] == state.shape[2]
    assert left_bath.shape[1] == ham.shape[0] and right_bath.shape[1] == ham.shape[3]

    # the optimal contraction order depends on the details
    # this order seems to be pretty balanced, but needs to be
    # revisited when use-cases are more well-known
    state = torch.tensordot(left_bath, state, 1)
    state = state.permute(0, 3, 1, 2)
    ham = ham.permute(0, 2, 1, 3)
    state = state.view(state.shape[0], state.shape[1], -1).contiguous()
    ham = ham.contiguous().view(-1, ham.shape[2], ham.shape[3])
    state = torch.tensordot(state, ham, 1)
    state = state.permute(0, 2, 1, 3)
    state = state.contiguous().view(state.shape[0], state.shape[1], -1)
    right_bath = right_bath.permute(2, 1, 0)
    right_bath = right_bath.contiguous().view(-1, right_bath.shape[2])
    state = torch.tensordot(state, right_bath, 1)
    return state


_TIME_CONVERSION_COEFF = 0.001  # Omega and delta are given in rad/μs, dt in ns


def evolve_pair(
    *,
    state_factors: list[torch.Tensor],
    baths: tuple[torch.Tensor, torch.Tensor],
    ham_factors: list[torch.Tensor],
    dt: float,
    orth_center_right: bool,
    is_hermitian: bool,
    config: MPSConfig,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Time evolution of a pair of tensors of a tensor train using baths and truncated SVD.
    Returned state tensors are kept on their respective devices.

    The input state tensor objects become invalid after calling that function.
    """

    time_step = -1j * _TIME_CONVERSION_COEFF * dt
    combined_state_factors, right_device, op = make_op(
        time_step=time_step,
        state_factors=state_factors,
        baths=baths,
        ham_factors=ham_factors,
    )
    left_bond_dim = combined_state_factors.shape[0]
    right_bond_dim = combined_state_factors.shape[-1]

    evol = krylov_exp(
        op,
        combined_state_factors,
        exp_tolerance=config.precision * config.extra_krylov_tolerance,
        norm_tolerance=config.precision * config.extra_krylov_tolerance,
        max_krylov_dim=config.max_krylov_dim,
        is_hermitian=is_hermitian,
    ).view(left_bond_dim * 2, 2 * right_bond_dim)

    l, r = split_tensor(
        evol,
        max_error=config.precision,
        max_rank=config.max_bond_dim,
        orth_center_right=orth_center_right,
    )

    return l.view(left_bond_dim, 2, -1), r.view(-1, 2, right_bond_dim).to(right_device)


def evolve_single(
    *,
    state_factor: torch.Tensor,
    baths: tuple[torch.Tensor, torch.Tensor],
    ham_factor: torch.Tensor,
    dt: float,
    is_hermitian: bool,
    config: MPSConfig,
) -> torch.Tensor:
    """
    Time evolution of a single tensor of a tensor train using baths.

    The input state tensor object becomes invalid after calling that function.
    """
    assert len(baths) == 2

    left_bath, right_bath = baths

    def op(x: torch.Tensor) -> torch.Tensor:
        return (
            -_TIME_CONVERSION_COEFF
            * 1j
            * dt
            * apply_effective_Hamiltonian(
                x,
                ham_factor,
                left_bath,
                right_bath,
            )
        )

    return krylov_exp(
        op,
        state_factor,
        exp_tolerance=config.precision * config.extra_krylov_tolerance,
        norm_tolerance=config.precision * config.extra_krylov_tolerance,
        max_krylov_dim=config.max_krylov_dim,
        is_hermitian=is_hermitian,
    )


def minimize_energy_pair(
    *,
    state_factors: Sequence[torch.Tensor],
    baths: tuple[torch.Tensor, torch.Tensor],
    ham_factors: Sequence[torch.Tensor],
    orth_center_right: bool,
    config: MPSConfig,
    residual_tolerance: float,
) -> tuple[torch.Tensor, torch.Tensor, float]:
    """
    Minimizes the state factors (ψ_i, ψ_{i+1}) using the Lanczos/Arnoldi method
    """

    time_step = 1.0
    combined_state_factors, right_device, op = make_op(
        time_step=time_step,
        state_factors=state_factors,
        baths=baths,
        ham_factors=ham_factors,
    )

    left_bond_dim = combined_state_factors.shape[0]
    right_bond_dim = combined_state_factors.shape[-1]

    updated_state, updated_energy = krylov_energy_minimization(
        op,
        combined_state_factors,
        norm_tolerance=config.precision * config.extra_krylov_tolerance,
        residual_tolerance=residual_tolerance,
        max_krylov_dim=config.max_krylov_dim,
    )
    updated_state = updated_state.view(left_bond_dim * 2, 2 * right_bond_dim)

    l, r = split_tensor(
        updated_state,
        max_error=config.precision,
        max_rank=config.max_bond_dim,
        orth_center_right=orth_center_right,
    )

    return (
        l.view(left_bond_dim, 2, -1),
        r.view(-1, 2, right_bond_dim).to(right_device),
        updated_energy,
    )
