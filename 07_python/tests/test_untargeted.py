"""Hand-calculated checks of the markup decomposition and the moving average."""
import unittest
import numpy as np
from qmp.untargeted import centred_moving_average, markup_decomposition


def economy(mu, s, p, y):
    """Period-1 firm arrays for one market; period 2 holds unused filler."""
    def two_periods(values):
        first = np.asarray(values, dtype=float).reshape(-1, 1)
        return np.stack((first, np.full_like(first, 9.)), axis=2)
    return {"mu_ijt": two_periods(mu), "s_ijt": two_periods(s),
            "p_ijt": two_periods(p), "y_ijt": two_periods(y)}


class TestMarkupDecomposition(unittest.TestCase):
    def setUp(self):
        # Firm A continues, B exits and C enters in a new third slot.
        self.before = economy(mu=[1.5, 2.0], s=[.6, .4], p=[1., 1.], y=[6., 4.])
        self.after = economy(mu=[1.6, 0., 1.8], s=[.5, 0., .5], p=[1., 0., 1.], y=[5., 0., 5.])

    def test_hand_calculated_parts(self):
        result = markup_decomposition(self.before, self.after)
        self.assertAlmostEqual(result["mu_bar"][0], 1.7)
        self.assertAlmostEqual(result["mu_bar"][1], 1.7)
        self.assertAlmostEqual(result["total"], 0.)
        self.assertAlmostEqual(result["within"], .06)
        self.assertAlmostEqual(result["share"], .02)
        self.assertAlmostEqual(result["cross"], -.01)
        self.assertAlmostEqual(result["reallocation"], .01)
        self.assertAlmostEqual(result["net_entry"], .05 - .12)
        self.assertAlmostEqual(result["error"], 0.)

    def test_parts_add_up_with_entry_and_exit(self):
        rng = np.random.default_rng(7)
        shape = (6, 40)
        arrays = []
        for _ in range(2):
            active = rng.random(shape) > .3
            s = np.where(active, rng.random(shape), 0.)
            arrays.append({"mu_ijt": np.dstack([np.where(active, 1.2 + rng.random(shape), 0.)] * 2),
                           "s_ijt": np.dstack([s] * 2),
                           "p_ijt": np.dstack([np.where(active, .5 + rng.random(shape), 0.)] * 2),
                           "y_ijt": np.dstack([np.where(active, rng.random(shape), 0.)] * 2)})
        result = markup_decomposition(*arrays)
        self.assertLess(abs(result["error"]), 1e-14)
        self.assertAlmostEqual(result["total"], result["mu_bar"][1] - result["mu_bar"][0])

    def test_inactive_and_nonfinite_firms_are_excluded(self):
        before = economy(mu=[1.5, np.nan], s=[1., .2], p=[1., 1.], y=[2., 3.])
        after = economy(mu=[1.7, 1.9], s=[1., -1.], p=[1., 1.], y=[2., 3.])
        result = markup_decomposition(before, after)
        self.assertEqual(result["mu_bar"], (1.5, 1.7))
        self.assertAlmostEqual(result["within"], .2)
        self.assertAlmostEqual(result["net_entry"], 0.)

    def test_inputs_are_not_modified(self):
        copies = [{k: v.copy() for k, v in e.items()} for e in (self.before, self.after)]
        markup_decomposition(self.before, self.after)
        for original, copy in zip((self.before, self.after), copies):
            for key in copy:
                np.testing.assert_array_equal(original[key], copy[key])

    def test_economies_without_sales_or_with_other_markets_are_rejected(self):
        empty = economy(mu=[0.], s=[0.], p=[0.], y=[0.])
        with self.assertRaises(ValueError):
            markup_decomposition(self.before, empty)
        wider = {k: np.concatenate((v, v), axis=1) for k, v in self.after.items()}
        with self.assertRaises(ValueError):
            markup_decomposition(self.before, wider)


class TestCentredMovingAverage(unittest.TestCase):
    def test_endpoints_use_the_available_years(self):
        np.testing.assert_allclose(centred_moving_average([1, 2, 3, 4, 5, 6]),
                                   [2, 2.5, 3, 4, 4.5, 5])
        np.testing.assert_allclose(centred_moving_average([1, 2, 3], order=1), [1, 2, 3])

    def test_missing_values_are_skipped(self):
        np.testing.assert_allclose(centred_moving_average([1, np.nan, 3], order=3), [1, 2, 3])
        self.assertTrue(np.isnan(centred_moving_average([np.nan, 1.], order=1)[0]))

    def test_order_must_be_a_positive_odd_integer(self):
        for order in (0, 2, 2.5, -1):
            with self.assertRaises(ValueError):
                centred_moving_average([1, 2, 3], order=order)


if __name__ == "__main__":
    unittest.main()
