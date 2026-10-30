"""Hand-calculated checks of the three statistics shown to students."""
import unittest
import numpy as np
from qmp.moments import compute_moments


class TestCourseMoments(unittest.TestCase):
    def setUp(self):
        self.equi = {
            "n_ijt": np.array([[[1., 2.]], [[3., 0.]]]),
            "phi_ijt": np.array([[[.2, .2]], [[.4, 0.]]]),
            "p_ijt": np.ones((2, 1, 2)),
            "y_ijt": np.array([[[4., 5.]], [[6., 0.]]]),
            "mu_ijt": np.array([[[1.5, 1.5]], [[2., 0.]]]),
            "W_t": np.array([2., 2.]),
        }

    def test_hand_calculated_flows_and_weights(self):
        result = compute_moments(self.equi, gamma=1., alpha_cogs=.8, psi_cogs=.5, psi_sga=.25)
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(result["employment_reallocation_rate"], 4.4/3.4)
        self.assertAlmostEqual(result["markup_sales_weighted"], 1.8)
        expected = .4*1.6/6.6 + .6*3.2/18.2
        self.assertAlmostEqual(result["sga_cost_share_sales_weighted"], expected)
        self.assertNotAlmostEqual(expected, (1.6+3.2)/(6.6+18.2))

    def test_does_not_modify_firm_arrays(self):
        before = {k:v.copy() for k,v in self.equi.items()}
        compute_moments(self.equi)
        for key in before:
            np.testing.assert_array_equal(before[key], self.equi[key])

    def test_empty_economy_is_rejected(self):
        self.equi["n_ijt"][:] = 0
        with self.assertRaises(ValueError):
            compute_moments(self.equi)


if __name__ == "__main__":
    unittest.main()
