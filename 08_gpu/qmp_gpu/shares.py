"""Strict float64 CUDA market shares, matching the frozen NumPy iteration."""
from __future__ import annotations

import torch
from qmp.equilibrium import EquilibriumError, Numerics


def solve_shares(z, theta: float, eta: float, gamma: float, numerics=None):
    """Freeze converged markets individually; zeros represent inactive firms.

    Empty markets and monopolies have explicit solutions. Returned markups use
    the last pre-damping shares, exactly as the NumPy reference does. Every
    array operation remains on the input CUDA device.
    """
    n = numerics or Numerics()
    if not isinstance(z, torch.Tensor) or z.device.type != 'cuda' or z.dtype != torch.float64:
        raise ValueError('z must be a CUDA float64 tensor')
    if z.ndim != 2 or not bool(torch.isfinite(z).all()) or bool((z < 0).any()):
        raise ValueError('z must be a finite, nonnegative two-dimensional array')
    if not 1 < theta <= eta or not 0 < gamma < eta / (eta - 1):
        raise ValueError('invalid demand parameters or returns to scale')
    if not 0 < n.share_damping <= 1 or not 0 < n.share_tol < 1 or n.share_max_iter < 1:
        raise ValueError('invalid share iteration controls')
    active = z > 0
    count = active.sum(dim=0)
    total = z.sum(dim=0)
    s = z / torch.where(total > 0, total, 1.0)
    mu = torch.zeros_like(z)
    iterations = torch.zeros(z.shape[1], dtype=torch.int64, device=z.device)
    residual = torch.zeros(z.shape[1], dtype=z.dtype, device=z.device)
    done = count == 0
    monopoly = count == 1
    # Casting before scalar arithmetic prevents bool-to-float32 promotion.
    mu = torch.where(monopoly[None, :], active.to(z.dtype) * theta / (theta - 1), mu)
    iterations = torch.where(monopoly, 1, iterations)
    done = done | monopoly
    z_inverse = torch.where(active, torch.where(active, z, 1.0) ** (-1 / gamma), 0.0)
    exponent = gamma * (1 - eta) / (gamma - gamma * eta + eta)

    def update(shares):
        elasticity = 1 / (shares / theta + (1 - shares) / eta)
        markups = elasticity / (elasticity - 1)
        product = torch.where(active, markups * z_inverse, 1.0)
        weight = torch.where(active, product ** exponent, 0.0)
        denominator = weight.sum(dim=0)
        proposed = weight / torch.where(denominator > 0, denominator, 1.0)
        return proposed, torch.where(active, markups, 0.0)

    for iteration in range(1, n.share_max_iter + 1):
        if bool(done.all()):
            break
        proposed, current_mu = update(s)
        denominator = torch.linalg.vector_norm(s, dim=0)
        distance = torch.linalg.vector_norm(proposed - s, dim=0) / torch.where(denominator > 0, denominator, 1.0)
        working = ~done
        relaxed = n.share_damping * proposed + (1 - n.share_damping) * s
        normalizer = relaxed.sum(dim=0)
        relaxed = relaxed / torch.where(normalizer > 0, normalizer, 1.0)
        s = torch.where(working[None, :], relaxed, s)
        mu = torch.where(working[None, :], current_mu, mu)
        iterations = torch.where(working, iteration, iterations)
        residual = torch.where(working, distance, residual)
        done = done | (working & (distance < n.share_tol))
    if not bool(done.all()):
        failed = ~done
        raise EquilibriumError(
            f'share fixed point failed in {int(failed.sum().item())} markets after '
            f'{n.share_max_iter} iterations; maximum relative residual {float(residual[failed].max().item()):.3g}'
        )
    proposed, _ = update(s)
    denominator = torch.linalg.vector_norm(s, dim=0)
    returned = torch.linalg.vector_norm(proposed - s, dim=0) / torch.where(denominator > 0, denominator, 1.0)
    if not bool(torch.isfinite(s).all() & torch.isfinite(mu).all()):
        raise EquilibriumError('nonfinite shares or markups')
    return s, mu, {'iterations': iterations, 'stopping_residual': residual,
                   'returned_residual': returned}
