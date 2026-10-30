"""Independent CUDA-array implementation of the full teaching economy."""
from .equilibrium import EquilibriumError, ModelConfig, Numerics, prepare_inputs, solve_economy
from .shares import solve_shares

__all__ = ['EquilibriumError', 'ModelConfig', 'Numerics', 'prepare_inputs',
           'solve_economy', 'solve_shares', 'simulate']


def simulate(x, *, config=None, numerics=None, draws=None, device='cuda', prepared_inputs=None):
    """Return CUDA equilibrium arrays, three course moments and diagnostics."""
    from .moments import compute_moments
    c = config or ModelConfig()
    result = solve_economy(x, config=c, numerics=numerics, draws=draws, device=device,
                           prepared_inputs=prepared_inputs)
    result['moments'] = compute_moments(result['equi'], gamma=c.gamma, alpha_cogs=c.alpha_cogs,
                                        psi_cogs=c.psi_cogs, psi_sga=c.psi_sga)
    result['diagnostics']['entry_stopping_rule_met'] = all(
        period['entry_stopping_rule_met'] for period in result['diagnostics']['periods'])
    return result
