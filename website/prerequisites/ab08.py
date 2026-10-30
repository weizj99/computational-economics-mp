"""A small AB08 pricing exercise: one sector, constant returns, fixed firms.

Our own Python teaching implementation, informed by Chris Edmond's Lecture 19
(2014), pp. 4--10: https://www.chrisedmond.net/phd2014/90065_lecture19.pdf
This is not the full AB08 model or the course's general-equilibrium engine.
Run: python ab08.py [--self-test]
Requires only NumPy.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Sector:
    shares: np.ndarray
    elasticities: np.ndarray
    markups: np.ndarray
    prices: np.ndarray
    iterations: int
    residual: float


def elasticities(shares, theta=1.5, eta=5.0, conduct="cournot"):
    """theta: across-sector substitution; eta: within-sector substitution."""
    s = np.asarray(shares, dtype=float)
    if not np.isfinite([theta, eta]).all() or not eta > theta > 1:
        raise ValueError("Require finite eta > theta > 1.")
    if not np.isfinite(s).all() or np.any((s < 0) | (s > 1)):
        raise ValueError("Shares must be finite and between zero and one.")
    if conduct == "cournot":
        return 1.0 / (s / theta + (1.0 - s) / eta)
    if conduct == "bertrand":
        return s * theta + (1.0 - s) * eta
    raise ValueError("conduct must be 'cournot' or 'bertrand'.")


def solve_sector(productivity, theta=1.5, eta=5.0, conduct="cournot",
                 tolerance=1e-12, damping=0.25, max_iterations=10000):
    """Solve shares = CES_shares(markup(shares) / productivity).

    Unit factor cost is one, so constant-returns marginal cost is 1 / z.
    The stopping rule checks the *undamped* relative fixed-point residual.
    Failure to converge raises an error rather than returning a guess.
    """
    z = np.asarray(productivity, dtype=float)
    if z.ndim != 1 or z.size == 0 or not np.isfinite(z).all() or np.any(z <= 0):
        raise ValueError("productivity must be a nonempty positive finite vector.")
    if not 0 < damping <= 1 or not tolerance > 0 or max_iterations < 1:
        raise ValueError("Invalid numerical settings.")
    s = z / z.sum()
    for iteration in range(1, max_iterations + 1):
        eps = elasticities(s, theta, eta, conduct)
        mu = eps / (eps - 1.0)
        p = mu / z
        # Subtracting the maximum keeps large powers numerically stable.
        log_weights = (1.0 - eta) * np.log(p)
        weights = np.exp(log_weights - log_weights.max())
        implied_s = weights / weights.sum()
        residual = float(np.linalg.norm(implied_s - s) / np.linalg.norm(s))
        if residual <= tolerance:
            return Sector(s, eps, mu, p, iteration, residual)
        s = (1.0 - damping) * s + damping * implied_s
        s /= s.sum()
    raise RuntimeError(f"Share iteration did not converge: residual={residual:.3g}")


def self_test():
    """Closed-form and residual checks; no external reference files required."""
    for conduct in ("cournot", "bertrand"):
        monopoly = solve_sector([2.0], conduct=conduct)
        np.testing.assert_allclose(monopoly.shares, [1.0], atol=1e-14)
        np.testing.assert_allclose(monopoly.markups, [3.0], atol=1e-14)
        symmetric = solve_sector(np.ones(4), conduct=conduct)
        eps = elasticities(np.full(4, 0.25), conduct=conduct)
        np.testing.assert_allclose(symmetric.shares, np.full(4, 0.25), atol=1e-14)
        np.testing.assert_allclose(symmetric.markups, eps / (eps - 1), atol=1e-14)
        unequal = solve_sector([1.6, 1.0, 0.8], conduct=conduct)
        assert unequal.residual <= 1e-12
        assert np.all(np.diff(unequal.shares) < 0)
        assert np.all(np.diff(unequal.markups) < 0)
        np.testing.assert_allclose(unequal.prices, unequal.markups / [1.6, 1, .8])
    # Cournot elasticity is a weighted harmonic mean; Bertrand is arithmetic.
    s = np.linspace(0, 1, 11)
    assert np.all(elasticities(s, conduct="cournot") <=
                  elasticities(s, conduct="bertrand") + 1e-14)
    try:
        solve_sector([1, 0])
    except ValueError:
        pass
    else:
        raise AssertionError("Nonpositive productivity should be rejected.")
    print("AB08 checks passed: monopoly, symmetry, both conduct rules, residuals.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    for conduct in ("cournot", "bertrand"):
        result = solve_sector([1.6, 1.0, 0.8], conduct=conduct)
        print(f"\n{conduct.title()} | theta=1.5, eta=5, z=[1.6, 1, .8]")
        print("firm    share     elasticity    markup     price")
        for i in range(3):
            print(f" {i + 1:>2}   {result.shares[i]:.6f}     "
                  f"{result.elasticities[i]:.6f}    {result.markups[i]:.6f}   "
                  f"{result.prices[i]:.6f}")
        print(f"Iterations: {result.iterations}; residual: {result.residual:.3e}")
