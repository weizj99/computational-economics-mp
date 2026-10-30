"""The three moments used by this course's estimation exercise.

Unused legacy statistics and duplicated output slots belong to the internal
cross-language validation adapter, not to this teaching interface.
"""
import numpy as np


def compute_moments(equi, *, gamma=1.0252, alpha_cogs=0.8365,
                    psi_cogs=0.33, psi_sga=0.33):
    """Return employment reallocation, sales-weighted markup and SGA/costs.

    Employment includes production and overhead labor. Costs include variable
    inputs, capital and overhead. The SGA moment is a sales-weighted mean of
    firm cost shares, rather than an aggregate SGA-to-total-cost ratio.
    """
    n = np.asarray(equi["n_ijt"], dtype=float)
    fixed = np.asarray(equi["phi_ijt"], dtype=float)
    if n.ndim != 3 or n.shape[-1] != 2 or fixed.shape != n.shape:
        raise ValueError("firm labor arrays must have matching (firms, markets, 2) shapes")
    employed = n > 0
    employment = np.where(employed, n + fixed, 0.0)
    mean_employment = 0.5 * employment.sum()
    if not np.isfinite(mean_employment) or mean_employment <= 0:
        raise ValueError("reallocation requires positive finite employment")
    reallocation = np.abs(employment[:, :, 1] - employment[:, :, 0]).sum() / mean_employment

    active = employed[:, :, 0]
    select = lambda a: np.asarray(a).ravel(order="F")[active.ravel(order="F")]
    revenue = select(equi["p_ijt"][:, :, 0] * equi["y_ijt"][:, :, 0])
    markup = select(equi["mu_ijt"][:, :, 0])
    wage = float(np.asarray(equi["W_t"]).ravel()[0])
    sga = wage * select(fixed[:, :, 0]) / psi_sga
    costs = gamma / alpha_cogs * wage * select(n[:, :, 0]) / psi_cogs + sga
    if not revenue.size or not np.isfinite(revenue).all() or revenue.sum() <= 0:
        raise ValueError("weighted moments require positive finite sales")
    if not np.isfinite(costs).all() or np.any(costs <= 0) or not np.isfinite(markup).all():
        raise ValueError("weighted moments require positive finite costs and finite markups")
    weights = revenue / revenue.sum()
    return {
        "employment_reallocation_rate": float(reallocation),
        "markup_sales_weighted": float(weights @ markup),
        "sga_cost_share_sales_weighted": float(weights @ (sga / costs)),
    }
