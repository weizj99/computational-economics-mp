"""Search-design, objective, checkpoint, and diagnostic-contract checks.

The model is mocked where appropriate: these tests check orchestration failure
modes rather than repeatedly solving an economy already covered by solver tests.
"""
import copy
import csv
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from qmp import estimation as E
from qmp.equilibrium import Numerics


def fixture_boxes():
    return {year: {"sigma_lo": .03, "sigma_hi": .11, "N_lo": 4.2, "N_hi": 8.2,
                   "zeta_lo": .4, "zeta_hi": 1.2} for year in E.YEARS}


def good_diagnostics():
    round_ = {"iteration": 1, "root_relative_residual": 1e-15,
              "max_share_residual": 5e-11, "max_share_stopping_residual": 8e-11,
              "labor_relative_residual": -1e-13, "max_share_iterations": 30}
    period = {**round_, "entry_iterations": 1, "entry_stopping_rule_met": True,
              "rounds": [round_]}
    return {"periods": [copy.deepcopy(period), copy.deepcopy(period)]}


def good_record(point, manifest):
    record = {key: point[key] for key in ("row_id", "year", "sigma", "N", "M", "zeta")}
    diagnostics = good_diagnostics()
    record.update(status="ok", moments=dict(zip(E.MOMENT_NAMES, [.3, 1.4, .15])), phi=1e-6,
                  Mbar=3.0, elapsed_seconds=1.0, diagnostics=diagnostics,
                  quality=E.diagnostic_quality(diagnostics, manifest["numerics"]), error=None,
                  point_fingerprint=E.object_hash(point), run_fingerprint=manifest["run_fingerprint"])
    return record


class TestSearchDesign(unittest.TestCase):
    def test_sobol_origin_first_points_and_excluded_upper_bounds(self):
        boxes = fixture_boxes()
        points = E.make_points(boxes)
        self.assertEqual(len(points), 22528)
        expected = np.array([[0., 0., 0.], [.5, .5, .5], [.25, .75, .25], [.75, .25, .75],
                             [.125, .625, .875], [.625, .125, .375], [.375, .375, .625], [.875, .875, .125]])
        lower, width = np.array([.03, 4.2, .4]), np.array([.08, 4., .8])
        np.testing.assert_array_equal(E.standard_sobol_points()[:8], expected)
        np.testing.assert_allclose([[point[p] for p in E.PARAMETERS] for point in points[:8]], lower + expected * width)
        for point in points:
            self.assertEqual(point["M"], int(np.floor(point["N"])))
            self.assertTrue(all(boxes[point["year"]][f"{p}_lo"] <= point[p] < boxes[point["year"]][f"{p}_hi"] for p in E.PARAMETERS))
        self.assertEqual([point["row_id"] for point in points], list(range(1, 22529)))
        self.assertEqual(points[0]["row_id"], 1)
        self.assertEqual(points[-1]["row_id"], 22528)
        self.assertEqual(points[512]["row_id"], 513)
        self.assertEqual(points[512]["year"], 1981)
        self.assertEqual(points[512]["sobol_index"], 0)
        self.assertEqual([points[1][p] for p in E.PARAMETERS], [points[513][p] for p in E.PARAMETERS])

    def test_historical_direction_numbers_all_nine_bits(self):
        # Independently tabulated direction numerators; binary powers isolate
        # each direction and detect a silent Joe–Kuo or Gray-order substitution.
        directions = np.array([[256, 128, 64, 32, 16, 8, 4, 2, 1],
                               [256, 384, 320, 480, 272, 408, 340, 510, 257],
                               [256, 128, 448, 352, 208, 488, 268, 158, 465]])
        unit = E.standard_sobol_points()
        np.testing.assert_array_equal(unit[[1 << bit for bit in range(9)]], directions.T / 512)
        self.assertEqual(len(np.unique(unit, axis=0)), 512)

    def test_weighted_loss_and_first_row_tie(self):
        def record(row_id, values, status="ok"):
            return {"row_id": row_id, "status": status, "moments": dict(zip(E.MOMENT_NAMES, values))}
        ranked = E.rank_records([record(9, [2., 3., 4.]), record(2, [2., 3., 4.]),
                                 record(0, [1., 1., 1.], "failed"), record(5, [2., 2., 2.])],
                                [1., 1., 1.], [2., 3., 4.])
        self.assertEqual([item[1] for item in ranked], [5, 2, 9])
        self.assertEqual([item[0] for item in ranked], [9., 50., 50.])

    def test_every_round_matters_and_signed_labor_error_is_absolute(self):
        diagnostics = good_diagnostics()
        self.assertTrue(E.diagnostic_quality(diagnostics, asdict(Numerics()))["passed"])
        bad = copy.deepcopy(diagnostics["periods"][0]["rounds"][0])
        bad["labor_relative_residual"] = -2e-10
        diagnostics["periods"][0]["rounds"].insert(0, bad)
        quality = E.diagnostic_quality(diagnostics, asdict(Numerics()))
        self.assertFalse(quality["passed"])
        self.assertEqual(quality["labor_relative_residual"], 2e-10)

    def test_entry_limit_and_missing_diagnostics_are_rejected(self):
        diagnostics = good_diagnostics()
        diagnostics["periods"][1]["entry_iterations"] = 50
        # The preserved rule can first meet proposed_drop < 3 on round 50.
        self.assertTrue(E.diagnostic_quality(diagnostics, asdict(Numerics()))["passed"])
        diagnostics["periods"][1]["entry_stopping_rule_met"] = False
        self.assertFalse(E.diagnostic_quality(diagnostics, asdict(Numerics()))["passed"])
        self.assertFalse(E.diagnostic_quality({}, asdict(Numerics()))["passed"])

    def test_share_cap_and_nonfinite_residual_are_rejected(self):
        for field, value in (("max_share_iterations", 1000), ("root_relative_residual", float("nan"))):
            diagnostics = good_diagnostics()
            diagnostics["periods"][0]["rounds"][0][field] = value
            self.assertFalse(E.diagnostic_quality(diagnostics, asdict(Numerics()))["passed"])


class TestRunIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = self.root / "data"
        self.run = self.root / "run"
        self.data.mkdir()
        target_rows = [{"year": year, "rer_total": .2 + index * .001,
                        "mu_w": 1.2 + index * .002, "mean_sga_tc_w": .1 + index * .003}
                       for index, year in enumerate(E.YEARS)]
        (self.data / "Moments.csv").write_bytes(E.csv_bytes(target_rows, ("year", *E.DATA_NAMES)))
        box_rows = [{"year": year, **box} for year, box in fixture_boxes().items()]
        (self.data / "boxes.csv").write_bytes(E.csv_bytes(box_rows, ("year", *fixture_boxes()[1980])))
        self.manifest = E.prepare(self.data, self.run)
        _, self.points = E.load_run(self.run)

    def test_sample_variance_uses_all_44_targets_and_ddof_one(self):
        # Sample variance of 0,...,43 is n(n+1)/12 = 165, before scaling.
        expected = [1.0 / (165 * scale**2) for scale in (.001, .002, .003)]
        np.testing.assert_allclose(self.manifest["weights"], expected, rtol=1e-14)
        self.assertEqual(self.manifest["point_count"], 22528)
        self.assertEqual(self.manifest["point_design"]["row_id_base"], 1)
        self.assertEqual(E.prepare(self.data, self.run), self.manifest)

    def test_mutated_frozen_data_and_points_are_rejected(self):
        target = self.run / "inputs" / "Moments.csv"
        original = target.read_bytes()
        target.write_bytes(original + b"\n")
        with self.assertRaisesRegex(E.ContractError, "input fingerprint"):
            E.load_run(self.run)
        target.write_bytes(original)
        with (self.run / "points.csv").open("ab") as handle:
            handle.write(b"\n")
        with self.assertRaisesRegex(E.ContractError, "point table fingerprint"):
            E.load_run(self.run)

    def test_source_and_environment_mismatch_are_rejected(self):
        with patch.object(E, "source_hashes", return_value={"changed": "source"}):
            with self.assertRaisesRegex(E.ContractError, "source code changed"):
                E.load_run(self.run)
        with patch.object(E, "runtime_versions", return_value={"changed": "version"}):
            with self.assertRaisesRegex(E.ContractError, "versions differ"):
                E.load_run(self.run)

    def test_checkpoint_signature_and_coordinate_mismatch_are_rejected(self):
        record = good_record(self.points[0], self.manifest)
        E.validate_record(record, self.points[0], self.manifest)
        record["sigma"] += 1e-5
        with self.assertRaisesRegex(E.ContractError, "mismatched sigma"):
            E.validate_record(record, self.points[0], self.manifest)
        record = good_record(self.points[0], self.manifest)
        record["run_fingerprint"] = "wrong"
        with self.assertRaisesRegex(E.ContractError, "run fingerprint"):
            E.validate_record(record, self.points[0], self.manifest)

    def test_incomplete_run_is_provisional_and_bad_rows_do_not_win(self):
        first = good_record(self.points[0], self.manifest)
        second = good_record(self.points[1], self.manifest)
        second.update(status="partial", error="entry iteration cap reached")
        second["moments"] = dict(zip(E.MOMENT_NAMES, self.manifest["targets"]["1980"]))
        for record in (first, second):
            E.atomic_write_json(self.run / "records" / f"{record['row_id']:05d}.json", record)
        summary = E.select(self.run)
        self.assertFalse(summary["complete"])
        self.assertTrue(summary["provisional"])
        self.assertFalse(summary["selection_valid"])
        self.assertEqual(summary["completed_records"], 2)
        self.assertEqual(len(summary["missing_records"]), 22526)
        self.assertEqual(summary["failed_records"][0]["row_id"], 2)
        with (self.run / "annual_estimates.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 44)
        self.assertEqual(rows[0]["row_id"], "1")
        self.assertEqual(rows[0]["sigma_pos"], "0.0")
        self.assertEqual(rows[1]["row_id"], "")

    def test_corrupt_checkpoint_is_reported_and_resume_stops(self):
        bad = good_record(self.points[0], self.manifest)
        bad["point_fingerprint"] = "wrong"
        E.atomic_write_json(self.run / "records" / "00001.json", bad)
        summary = E.select(self.run)
        self.assertEqual(summary["corrupt_records"][0]["row_id"], 1)
        self.assertEqual(summary["completed_records"], 0)
        with self.assertRaises(E.ContractError):
            E.solve(self.run, shard_index=0, shard_count=22528, limit=1)

    def test_shards_resume_and_exceptions_are_durable_failures(self):
        # Two points with identical M and an external shard make model mocking
        # sufficient to verify checkpoint identity and failure semantics.
        with patch.object(E, "generate_draws", return_value={}), patch.object(E, "simulate", side_effect=RuntimeError("test failure")) as model:
            counts = E.solve(self.run, shard_index=0, shard_count=22528)
            self.assertEqual(counts["failed"], 1)
            self.assertEqual(model.call_count, 1)
            again = E.solve(self.run, shard_index=0, shard_count=22528)
            self.assertEqual(again["resumed"], 1)
            self.assertEqual(model.call_count, 1)
        record = json.loads((self.run / "records" / "00001.json").read_text())
        self.assertEqual(record["row_id"], 1)
        self.assertEqual(record["status"], "failed")
        self.assertIsNone(record["moments"])
        self.assertIn("test failure", record["error"])


if __name__ == "__main__":
    unittest.main()
