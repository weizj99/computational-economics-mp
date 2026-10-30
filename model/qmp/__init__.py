"""Independent Python teaching implementation: one economy and course moments."""
from .draws import generate_draws
from .equilibrium import EquilibriumError, ModelConfig, Numerics, solve_economy
from .moments import compute_moments

__all__ = ["EquilibriumError", "ModelConfig", "Numerics", "solve_economy",
           "generate_draws", "compute_moments", "simulate"]


def simulate(x, *, config=None, numerics=None, draws=None):
    """Return equilibrium arrays, three named course moments, and diagnostics.

    The output includes an entry-rule status. A successful numerical solve
    does not establish a Nash entry
    equilibrium: the preserved sequential-exit rule does not test reentry.
    """
    config = config or ModelConfig()
    result = solve_economy(x, config=config, numerics=numerics, draws=draws)
    result["moments"] = compute_moments(
        result["equi"], gamma=config.gamma, alpha_cogs=config.alpha_cogs,
        psi_cogs=config.psi_cogs, psi_sga=config.psi_sga,
    )
    result["diagnostics"]["entry_stopping_rule_met"] = all(
        p["entry_stopping_rule_met"] for p in result["diagnostics"]["periods"]
    )
    return result
