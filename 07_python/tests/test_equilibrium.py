"""Numerical and economic checks that do not require any reference files."""

from dataclasses import replace
import unittest

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from scipy.optimize import brentq

from qmp.draws import generate_draws
from qmp.moments import compute_moments
from qmp.equilibrium import (
    EquilibriumError, ModelConfig, Numerics, _solve_output, solve_economy,
    solve_shares,
)


PARAMETERS = np.array([1.13125, 4.36875, .9, .06, 12., .7])
SMALL = ModelConfig(markets=60)


class TestMarketShares(unittest.TestCase):
    def test_empty_market_monopoly_and_symmetric_duopoly(self):
        z = np.array([[0., 2., 3.], [0., 0., 3.]])
        shares, markups, diagnostic = solve_shares(z, 1.2, 4., 1.03)
        assert_array_equal(shares, [[0., 1., .5], [0., 0., .5]])
        assert_allclose(markups, [[0., 6., 24/11], [0., 0., 24/11]])
        assert_array_equal(diagnostic["iterations"], [0, 1, 1])
        assert_allclose(diagnostic["returned_residual"], 0, atol=1e-15)

    def test_asymmetric_duopoly_against_independent_scalar_solution(self):
        # At constant returns, prices are markup/productivity. Combine CES
        # demand with Cournot elasticity and solve the single share directly.
        theta, eta = 1.2, 4.
        z1, z2 = 1.0, 1.7

        def markup(s):
            return 1 / (1 - s/theta - (1-s)/eta)

        def excess_share(s):
            p1, p2 = markup(s)/z1, markup(1-s)/z2
            demand_share = p1**(1-eta) / (p1**(1-eta) + p2**(1-eta))
            return s - demand_share

        independent = brentq(excess_share, .001, .999, xtol=1e-14)
        shares, markups, diagnostic = solve_shares(np.array([[z1], [z2]]), theta, eta, 1.)
        assert_allclose(shares[:, 0], [independent, 1-independent], atol=1e-10, rtol=0)
        assert_allclose(markups[:, 0], [markup(independent), markup(1-independent)], atol=1e-10, rtol=0)
        self.assertLess(diagnostic["returned_residual"].max(), 1e-10)

    def test_nonconvergence_raises_instead_of_returning_last_iterate(self):
        with self.assertRaisesRegex(EquilibriumError, "share fixed point failed"):
            solve_shares(np.array([[1.], [2.]]), 1.2, 4., 1.03,
                         Numerics(share_max_iter=1))


class TestOutputRoot(unittest.TestCase):
    @staticmethod
    def solve_with_coefficients(config, k2, overhead, numerics=None):
        # Choose wc=1 and scale production demand so the test economy has the
        # stated K2. These fixtures have roots known without a root finder.
        ac, ak = config.alpha_cogs, config.gamma - config.alpha_cogs
        coefficient = config.psi_cogs * (config.r * ac / ak)**(ak / config.gamma)
        return _solve_output(1., 1, k2 / coefficient, overhead,
                             config, numerics or Numerics())

    def test_decreasing_returns_unique_root(self):
        # Y^(-1/3) - .025*Y^(4/3) - .1 = 0 has Y=8.
        c = ModelConfig(gamma=.8, alpha_cogs=.6, varphi=1.)
        y, residual, _ = self.solve_with_coefficients(c, .025, .1)
        self.assertAlmostEqual(y, 8., places=11)
        self.assertLess(residual, 1e-12)

    def test_constant_returns_linear_root(self):
        # 1 - .4*Y - .2 = 0.
        c = ModelConfig(gamma=1., alpha_cogs=.8)
        y, residual, _ = self.solve_with_coefficients(c, .4, .2)
        self.assertAlmostEqual(y, 2., places=12)
        self.assertLess(residual, 1e-12)

    def test_increasing_returns_selects_upper_of_two_positive_roots(self):
        # Let v=Y^(1/4). Then v-v^3-.288=0; v=.8 is the upper
        # positive root, and its Y value is .4096. The lower root differs.
        c = ModelConfig(gamma=1.2, alpha_cogs=.8, varphi=1.)
        y, residual, _ = self.solve_with_coefficients(c, 1., .288)
        self.assertAlmostEqual(y, .8**4, places=12)
        self.assertGreater(y, (1/np.sqrt(3))**4)
        self.assertLess(residual, 1e-12)

    def test_zero_overhead_uses_positive_root(self):
        c = ModelConfig(gamma=1.2, alpha_cogs=.8, varphi=1.)
        y, residual, _ = self.solve_with_coefficients(c, 1., 0.)
        self.assertAlmostEqual(y, 1., places=12)
        self.assertLess(residual, 1e-12)

    def test_infeasible_overhead_and_iteration_failure_are_explicit(self):
        c = ModelConfig(gamma=1.2, alpha_cogs=.8, varphi=1.)
        with self.assertRaisesRegex(EquilibriumError, "no upper positive output root"):
            self.solve_with_coefficients(c, 1., 2.)
        with self.assertRaisesRegex(EquilibriumError, "aggregate output solver failed"):
            self.solve_with_coefficients(c, 1., .288, Numerics(root_max_iter=1))


class TestNativeEconomy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = solve_economy(PARAMETERS, SMALL)

    def test_independent_labor_market_accounting(self):
        eq = self.result["equi"]
        labor_from_firms = (eq["n_ijt"] + eq["phi_ijt"]).sum(axis=(0, 1))
        relative_error = (labor_from_firms - eq["Ns_t"]) / eq["Ns_t"]
        assert_allclose(relative_error, 0, atol=1e-10, rtol=0)
        # Do not verify the identity using Nprod=Ns-overhead: that would be
        # tautological and would miss errors in firm labor demand.
        for t, period in enumerate(self.result["diagnostics"]["periods"]):
            self.assertLess(period["root_relative_residual"], 1e-12)
            self.assertAlmostEqual(period["labor_relative_residual"], relative_error[t], places=13)

    def test_market_shares_activity_and_all_inactive_quantities(self):
        eq = self.result["equi"]
        active = eq["z_ijt"] > 0
        occupied = active.any(axis=0)
        assert_allclose(eq["s_ijt"].sum(axis=0), occupied.astype(float), atol=1e-14, rtol=0)
        assert_array_equal(eq["Njt"], active.sum(axis=0))
        for key in ("phi_ijt", "mu_ijt", "s_ijt", "y_ijt", "p_ijt", "u_ijt", "n_ijt"):
            self.assertTrue(np.isfinite(eq[key]).all(), key)
            assert_array_equal(eq[key][~active], np.zeros((~active).sum()), err_msg=key)

    def test_reallocation_equals_absolute_firm_employment_changes(self):
        eq = self.result["equi"]
        employment = eq["n_ijt"] + eq["phi_ijt"]
        change = employment[:, :, 1] - employment[:, :, 0]
        expected = np.abs(change).sum() / (employment.sum() / 2)
        measured = compute_moments(eq, gamma=SMALL.gamma, alpha_cogs=SMALL.alpha_cogs,
                                   psi_cogs=SMALL.psi_cogs, psi_sga=SMALL.psi_sga)
        self.assertAlmostEqual(measured["employment_reallocation_rate"], expected, places=13)
        # This includes entrants and exiters through their zero employment in
        # the other period; their positions must not be compacted or reordered.
        self.assertGreater(np.count_nonzero((employment[:, :, 0] > 0) != (employment[:, :, 1] > 0)), 0)

    def test_local_generator_is_repeatable_and_does_not_touch_global_rng(self):
        global_before = np.random.get_state()
        first = generate_draws(12, 60, seed=100)
        second = generate_draws(12, 60, seed=100)
        other = generate_draws(12, 60, seed=101)
        for key in first:
            assert_array_equal(first[key], second[key])
        self.assertFalse(np.array_equal(first["eps_z1"], other["eps_z1"]))
        repeated = solve_economy(PARAMETERS, SMALL)
        assert_array_equal(repeated["equi"]["Y_t"], self.result["equi"]["Y_t"])
        assert_array_equal(repeated["equi"]["z_ijt"], self.result["equi"]["z_ijt"])
        global_after = np.random.get_state()
        self.assertEqual(global_before[0], global_after[0])
        assert_array_equal(global_before[1], global_after[1])
        self.assertEqual(global_before[2:], global_after[2:])

    def test_injected_draws_and_parameters_are_not_mutated(self):
        draws = generate_draws(12, 60, seed=100)
        original = {key: value.copy() for key, value in draws.items()}
        for value in draws.values():
            value.setflags(write=False)
        parameters = PARAMETERS.copy()
        parameters.setflags(write=False)
        result = solve_economy(parameters, SMALL, draws=draws)
        assert_array_equal(result["equi"]["Y_t"], self.result["equi"]["Y_t"])
        assert_array_equal(parameters, PARAMETERS)
        for key in draws:
            assert_array_equal(draws[key], original[key])

    def test_draw_stream_matches_saved_results(self):
        # Values drawn by the code that produced the saved results. A change
        # here means the saved results no longer reproduce.
        draws = generate_draws(12, 60, seed=100)
        self.assertEqual(sorted(draws), ["eps_z1", "eps_z2"])
        assert_array_equal(draws["eps_z1"][0, :2], [1.63737399821164, -0.9164803775670456])
        assert_array_equal(draws["eps_z2"][-1, -2:], [0.7001492469907332, -0.9766767373595282])

    def test_missing_draws_are_an_error(self):
        with self.assertRaisesRegex(ValueError, "eps_z2"):
            solve_economy(PARAMETERS, SMALL, draws={"eps_z1": generate_draws(12, 60)["eps_z1"]})

    def test_entry_cap_is_reported_and_preserves_pre_exit_state(self):
        result = solve_economy(PARAMETERS, SMALL, Numerics(entry_max_iter=1))
        for period in result["diagnostics"]["periods"]:
            self.assertEqual(period["entry_stop_reason"], "iteration_limit")
            self.assertFalse(period["entry_stopping_rule_met"])
            self.assertGreaterEqual(period["proposed_drop"], 3)
            self.assertEqual(period["active_firms"], 12 * SMALL.markets)
            self.assertEqual(period["entry_rounds"], 1)
        self.assertTrue((result["equi"]["z_ijt"] > 0).all())

    def test_invalid_parameters_fail_before_simulation(self):
        for index, value in ((0, 1.), (1, 1.1), (2, 1.), (3, -.1),
                             (4, .9), (5, -.1), (3, np.nan)):
            x = PARAMETERS.copy()
            x[index] = value
            with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                solve_economy(x, SMALL)
        with self.assertRaisesRegex(ValueError, "6 finite parameters"):
            solve_economy(np.append(PARAMETERS, 0.), SMALL)
        for config in (replace(SMALL, gamma=.8), replace(SMALL, markets=0),
                       replace(SMALL, gamma=1.4), replace(SMALL, psi_sga=0)):
            with self.subTest(config=config), self.assertRaises(ValueError):
                solve_economy(PARAMETERS, config)
        with self.assertRaises(ValueError):
            solve_economy(PARAMETERS, SMALL, Numerics(share_damping=0))


if __name__ == "__main__":
    unittest.main()
