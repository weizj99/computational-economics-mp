"""The course's three moments, reduced on the equilibrium array's device.

This is the float64 tensor counterpart of ``qmp.moments.compute_moments``.
It preserves firm identity between periods and period-one sales weights.
Only the three returned scalar results are copied to the host.
"""
from __future__ import annotations

import torch


def compute_moments(equi, *, gamma=1.0252, alpha_cogs=0.8365,
                    psi_cogs=0.33, psi_sga=0.33):
    """Return reallocation, sales-weighted markup and weighted SGA/costs.

    Firm arrays have shape ``(firms, markets, 2)`` and use float64 on one
    device. Employment includes production and overhead labor only where
    production labor is positive. The SGA statistic is the sales-weighted
    mean of firm cost shares, not a ratio of aggregate SGA to aggregate cost.
    This function does not mutate its inputs or compact firms across time.
    """
    n = equi["n_ijt"]
    if not isinstance(n, torch.Tensor) or n.dtype != torch.float64:
        raise TypeError("firm labor arrays must be float64 tensors")

    def array(name):
        value = equi[name]
        if not isinstance(value, torch.Tensor) or value.dtype != torch.float64:
            raise TypeError(f"{name} must be a float64 tensor")
        if value.device != n.device:
            raise ValueError("equilibrium arrays must use the same device")
        return value

    fixed = array("phi_ijt")
    if n.ndim != 3 or n.shape[-1] != 2 or fixed.shape != n.shape:
        raise ValueError("firm labor arrays must have matching (firms, markets, 2) shapes")
    employed = n > 0
    employment = torch.where(employed, n + fixed, 0.0)
    mean_employment = 0.5 * employment.sum()
    if not bool(torch.isfinite(mean_employment) & (mean_employment > 0)):
        raise ValueError("reallocation requires positive finite employment")
    reallocation = torch.abs(employment[:, :, 1] - employment[:, :, 0]).sum() / mean_employment

    # NumPy's reference selects ravel(order="F"). Keep that logical order
    # instead of allowing a changed flattening convention to hide a mismatch.
    active = employed[:, :, 0].transpose(0, 1).reshape(-1)

    def select(value):
        return value.transpose(0, 1).reshape(-1)[active]

    price, quantity, firm_markup = array("p_ijt"), array("y_ijt"), array("mu_ijt")
    revenue = select(price[:, :, 0] * quantity[:, :, 0])
    markup = select(firm_markup[:, :, 0])
    wage = array("W_t").reshape(-1)[0]
    sga = wage * select(fixed[:, :, 0]) / psi_sga
    costs = gamma / alpha_cogs * wage * select(n[:, :, 0]) / psi_cogs + sga
    if revenue.numel() == 0 or not bool(torch.isfinite(revenue).all() & (revenue.sum() > 0)):
        raise ValueError("weighted moments require positive finite sales")
    if not bool(torch.isfinite(costs).all() & (costs > 0).all() & torch.isfinite(markup).all()):
        raise ValueError("weighted moments require positive finite costs and finite markups")
    weights = revenue / revenue.sum()
    values = torch.stack((reallocation, torch.dot(weights, markup), torch.dot(weights, sga / costs)))
    host_values = values.detach().cpu().tolist()
    return dict(zip(("employment_reallocation_rate", "markup_sales_weighted",
                     "sga_cost_share_sales_weighted"), host_values))
