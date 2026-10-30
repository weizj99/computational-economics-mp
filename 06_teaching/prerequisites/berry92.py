"""A small Berry-style complete-information entry exercise, entirely in Python.

Our own example accompanying Kawaguchi's Entry and Exit chapter/Assignment 6:
https://kohei-kawaguchi.github.io/EmpiricalIO/entryexit.html
https://kohei-kawaguchi.github.io/EmpiricalIO/assignment6.html
The profit specification is deliberately simplified; no airline data or
estimated parameters are used. Run: python berry92.py [--self-test]
Requires only NumPy. Exhaustive enumeration is for small teaching examples.
"""
from __future__ import annotations

import argparse
from itertools import product

import numpy as np


def _inputs(values, delta):
    v = np.asarray(values, dtype=float)
    if v.ndim != 1 or v.size == 0 or not np.isfinite(v).all():
        raise ValueError("values must be a nonempty finite vector.")
    if not np.isfinite(delta) or delta <= 0:
        raise ValueError("delta must be positive and finite.")
    return v


def operating_profit(values, n, delta=1.0):
    """Net profit conditional on operating with n total active firms."""
    v = _inputs(values, delta)
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("Conditional operating profit requires integer n >= 1.")
    return v - delta * np.log(n)


def deviation_gains(entered, values, delta=1.0):
    """Gain from switching one's action while every rival keeps its action.

    An incumbent can exit and earn zero; an outsider enters into n + 1 firms.
    Weak Nash conditions are gains <= 0. At exact zero-profit ties, distinct
    equilibrium counts can coexist; count uniqueness statements exclude ties.
    """
    v = _inputs(values, delta)
    raw = np.asarray(entered)
    if raw.shape != v.shape or not np.isin(raw, [False, True]).all():
        raise ValueError("entered must have one binary value for each firm.")
    active = raw.astype(bool)
    n = int(active.sum())
    gains = operating_profit(v, n + 1, delta)
    if n:
        gains[active] = -operating_profit(v, n, delta)[active]
    return gains


def pure_equilibria(values, delta=1.0, tolerance=1e-12):
    """Enumerate every pure-strategy Nash equilibrium of a small entry game."""
    v = _inputs(values, delta)
    if v.size > 20:
        raise ValueError("Enumeration is exponential; use at most 20 firms.")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative.")
    return [np.array(profile, dtype=bool)
            for profile in product((False, True), repeat=v.size)
            if np.all(deviation_gains(profile, v, delta) <= tolerance)]


def ranked_equilibrium(values, delta=1.0):
    """Construct one equilibrium by descending firm-specific profit index.

    The selected set consists of the highest indices. This construction uses
    the common crowding penalty delta*log(n); it is not a generic entry solver.
    Zero-profit candidates are included, a transparent selection convention.
    """
    v = _inputs(values, delta)
    order = np.argsort(-v, kind="stable")
    active = np.zeros(v.size, dtype=bool)
    for rank, firm in enumerate(order, start=1):
        if v[firm] - delta * np.log(rank) < 0:
            break
        active[firm] = True
    if np.any(deviation_gains(active, v, delta) > 1e-12):
        raise RuntimeError("The ranked candidate failed its deviation check.")
    return active


def self_test():
    v = np.array([1.4, 1.0, 0.9, 0.3])
    equilibria = pure_equilibria(v)
    sets = {tuple(np.flatnonzero(e)) for e in equilibria}
    assert sets == {(0, 1), (0, 2)}  # AB and AC: same count, different firms.
    np.testing.assert_array_equal(ranked_equilibrium(v), [True, True, False, False])
    assert not np.any(ranked_equilibrium([-1, -2]))
    assert np.all(ranked_equilibrium([3, 2, 1.5]))
    # Independent enumeration checks the fast ranking construction across cases.
    rng = np.random.default_rng(92)
    for _ in range(50):
        values = rng.normal(0.8, 0.6, 5)
        delta = rng.uniform(0.2, 1.8)
        equilibria = pure_equilibria(values, delta)
        ranked = ranked_equilibrium(values, delta)
        assert any(np.array_equal(ranked, e) for e in equilibria)
        assert len({int(e.sum()) for e in equilibria}) == 1
    # At an exact tie, both zero and one entrant may be weak equilibria.
    assert {int(e.sum()) for e in pure_equilibria([0.0])} == {0, 1}
    print("Berry checks passed: deviation conditions, multiplicity, 50 random games, ties.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    values = np.array([1.4, 1.0, 0.9, 0.3])
    labels = np.array(list("ABCD"))
    print("\nProfit: v_i - log(n); v=[1.4, 1.0, .9, .3]; outside option=0")
    for profile in pure_equilibria(values):
        print(f"Equilibrium: {''.join(labels[profile])}; "
              f"deviation gains [A,B,C,D]: {deviation_gains(profile, values).round(6)}")
    print("Ranked selection:", "".join(labels[ranked_equilibrium(values)]))
