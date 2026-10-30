"""Reproducible annual SMM search using the standalone NumPy economy.

Run ``python -m qmp.estimation --help``. Scheduler jobs divide the immutable
point table by row ID. Each completed point is an atomic checkpoint; no Torch,
pandas or private machine configuration is needed.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import uuid

import numpy as np
import scipy

from . import simulate
from .draws import generate_draws
from .equilibrium import ModelConfig, Numerics


SCHEMA_VERSION = 1
YEARS = tuple(range(1980, 2024))
POINTS_PER_YEAR = 512
PARAMETERS = ("sigma", "N", "zeta")
MOMENT_NAMES = (
    "employment_reallocation_rate", "markup_sales_weighted",
    "sga_cost_share_sales_weighted",
)
DATA_NAMES = ("rer_total", "mu_w", "mean_sga_tc_w")
FIXED = {"theta": 1.13125, "eta": 4.36875, "rho": 0.9}
SOURCE_FILES = ("__init__.py", "draws.py", "equilibrium.py", "moments.py", "estimation.py")
POINT_FIELDS = ("row_id", "year", "sobol_index", "sigma", "N", "M", "zeta")
RNG_CONTRACT = {
    "generator": "numpy.random.PCG64", "seed": 100,
    "scope": "reset seed for each M; reuse identical arrays for every point with that M",
    "draw_order": ["discarded(J,2)", "discarded(M,J)", "eps_z1(M,J)", "eps_z2(M,J)"],
    "dtype": "float64", "memory_order": "C",
}


class ContractError(RuntimeError):
    """Inputs, code, or a checkpoint do not match this immutable run."""


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def object_hash(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_hashes():
    directory = Path(__file__).resolve().parent
    return {name: file_hash(directory / name) for name in SOURCE_FILES}


def runtime_versions():
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}


def atomic_write_bytes(path, content):
    """Publish a flushed, complete file with an atomic rename on one filesystem."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        # Also make the rename durable on filesystems supporting directory fsync.
        if hasattr(os, "O_DIRECTORY"):
            descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path, value):
    atomic_write_bytes(path, (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8"))


def csv_bytes(rows, fields):
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return text.getvalue().encode("utf-8")


def read_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_inputs(data_dir):
    """Validate the exact 44 calendar years and finite, nondegenerate targets."""
    data_dir = Path(data_dir)
    targets, boxes = {}, {}
    for row in read_csv(data_dir / "Moments.csv"):
        year = int(row["year"])
        if year in targets:
            raise ContractError(f"duplicate target year {year}")
        targets[year] = [float(row[name]) for name in DATA_NAMES]
    for row in read_csv(data_dir / "boxes.csv"):
        year = int(row["year"])
        if year in boxes:
            raise ContractError(f"duplicate box year {year}")
        box = {f"{p}_{side}": float(row[f"{p}_{side}"]) for p in PARAMETERS for side in ("lo", "hi")}
        if not all(math.isfinite(v) for v in box.values()):
            raise ContractError(f"nonfinite box for {year}")
        if any(box[f"{p}_hi"] <= box[f"{p}_lo"] for p in PARAMETERS):
            raise ContractError(f"nonpositive box width for {year}")
        if box["N_lo"] < 1 or min(box["sigma_lo"], box["zeta_lo"]) < 0:
            raise ContractError(f"invalid parameter bounds for {year}")
        boxes[year] = box
    if sorted(targets) != list(YEARS) or sorted(boxes) != list(YEARS):
        raise ContractError("Moments.csv and boxes.csv must each contain 1980–2023 exactly once")
    values = np.asarray([targets[year] for year in YEARS], dtype=np.float64)
    variances = values.var(axis=0, ddof=1)
    if not np.isfinite(values).all() or not np.isfinite(variances).all() or np.any(variances <= 0):
        raise ContractError("target moments must be finite with positive sample variances")
    return targets, boxes, (1.0 / variances).tolist()


def standard_sobol_points():
    """The historical three-dimensional, standard-order Sobol 512-point net.

    Standard order uses the binary index directly, without a Gray transform.
    Directions use x+1, m=(1) in dimension 2 and x^2+x+1, m=(1,1)
    in dimension 3. The latter differs from SciPy's Joe–Kuo initialization.
    Integer arithmetic makes every unit-box coordinate an exact multiple of
    1/512. This construction needs no proprietary software or input file.
    """
    bits = 9
    directions = np.zeros((3, bits), dtype=np.uint64)
    for bit in range(bits):
        directions[0, bit] = 1 << (bits - bit - 1)
    directions[1, 0] = 1 << (bits - 1)
    for bit in range(1, bits):
        previous = int(directions[1, bit - 1])
        directions[1, bit] = previous ^ (previous >> 1)
    directions[2, 0], directions[2, 1] = 1 << (bits - 1), 1 << (bits - 2)
    for bit in range(2, bits):
        previous = int(directions[2, bit - 2])
        directions[2, bit] = previous ^ (previous >> 2) ^ int(directions[2, bit - 1])
    indices = np.arange(1 << bits, dtype=np.uint64)
    coordinates = np.zeros((len(indices), 3), dtype=np.uint64)
    for bit in range(bits):
        coordinates[((indices >> bit) & 1).astype(bool)] ^= directions[:, bit]
    return coordinates.astype(np.float64) / (1 << bits)


def make_points(boxes):
    """Identical, unscrambled standard-order Sobol net in every annual box.

    The zero point is included; all upper endpoints are excluded. N remains
    continuous in the table, while M=floor(N) determines potential firms.
    """
    unit = standard_sobol_points()
    rows = []
    for year in YEARS:
        lower = np.array([boxes[year][f"{p}_lo"] for p in PARAMETERS])
        upper = np.array([boxes[year][f"{p}_hi"] for p in PARAMETERS])
        values = lower + unit * (upper - lower)
        for index, (sigma, firms, zeta) in enumerate(values):
            rows.append({"row_id": len(rows) + 1, "year": year, "sobol_index": index,
                         "sigma": float(sigma), "N": float(firms), "M": math.floor(firms), "zeta": float(zeta)})
    return rows


def prepare(data_dir, run_dir):
    """Freeze data, parameter points, solver controls, code hashes, and weights."""
    data_dir, run_dir = Path(data_dir), Path(run_dir)
    targets, boxes, weights = read_inputs(data_dir)
    input_bytes = {name: (data_dir / name).read_bytes() for name in ("Moments.csv", "boxes.csv")}
    if (data_dir / "Untargeted_Moment.csv").exists():
        input_bytes["Untargeted_Moment.csv"] = (data_dir / "Untargeted_Moment.csv").read_bytes()
    points = make_points(boxes)
    point_bytes = csv_bytes(points, POINT_FIELDS)
    manifest = {
        "schema_version": SCHEMA_VERSION, "years": list(YEARS),
        "points_per_year": POINTS_PER_YEAR, "point_count": len(points),
        "point_design": {"method": "Sobol standard binary-index order", "dimension": 3, "scramble": False,
                         "m": 9, "skip": 0, "same_sequence_each_year": True,
                         "direction_polynomials": ["powers of one half", "x+1", "x^2+x+1"],
                         "initial_direction_numerators": [[], [1], [1, 1]],
                         "coordinate_order": list(PARAMETERS), "row_id_base": 1,
                         "upper_endpoints_included": False},
        "fixed_parameters": FIXED, "model_config": asdict(ModelConfig()), "numerics": asdict(Numerics()),
        "rng": RNG_CONTRACT, "quality_gates": {"labor_relative_residual": 1e-10,
          "all_rounds": True, "entry_stopping_rule_required": True, "iteration_caps_excluded": True},
        "moment_names": list(MOMENT_NAMES), "data_names": list(DATA_NAMES),
        "weights": weights, "weight_variance_ddof": 1,
        "targets": {str(year): targets[year] for year in YEARS},
        "boxes": {str(year): boxes[year] for year in YEARS},
        "inputs_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in input_bytes.items()},
        "points_sha256": hashlib.sha256(point_bytes).hexdigest(),
        "source_sha256": source_hashes(), "runtime_versions": runtime_versions(),
    }
    manifest["run_fingerprint"] = object_hash(manifest)
    if (run_dir / "manifest.json").exists():
        existing, _ = load_run(run_dir)
        if existing != manifest:
            raise ContractError("prepare would change an existing run; use a new run directory")
        return existing
    if (run_dir / "records").exists() and any((run_dir / "records").iterdir()):
        raise ContractError("records exist without a manifest; use a new run directory")
    for name, content in input_bytes.items():
        atomic_write_bytes(run_dir / "inputs" / name, content)
    atomic_write_bytes(run_dir / "points.csv", point_bytes)
    (run_dir / "records").mkdir(parents=True, exist_ok=True)
    atomic_write_json(run_dir / "manifest.json", manifest)
    return manifest


def load_run(run_dir):
    run_dir = Path(run_dir)
    with (run_dir / "manifest.json").open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    payload = {k: v for k, v in manifest.items() if k != "run_fingerprint"}
    if manifest.get("run_fingerprint") != object_hash(payload):
        raise ContractError("manifest fingerprint mismatch")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("unsupported manifest schema")
    if manifest["source_sha256"] != source_hashes():
        raise ContractError("source code changed since prepare; use the frozen code or a new run")
    if manifest["runtime_versions"] != runtime_versions():
        raise ContractError("Python/NumPy/SciPy versions differ from the prepared run")
    for name, expected in manifest["inputs_sha256"].items():
        if file_hash(run_dir / "inputs" / name) != expected:
            raise ContractError(f"input fingerprint mismatch: {name}")
    if file_hash(run_dir / "points.csv") != manifest["points_sha256"]:
        raise ContractError("point table fingerprint mismatch")
    points = []
    for row in read_csv(run_dir / "points.csv"):
        point = {key: int(row[key]) for key in ("row_id", "year", "sobol_index", "M")}
        point.update({key: float(row[key]) for key in PARAMETERS})
        if not all(math.isfinite(point[key]) for key in PARAMETERS) or point["M"] != math.floor(point["N"]):
            raise ContractError("invalid point coordinates")
        points.append(point)
    if manifest["point_design"]["row_id_base"] != 1:
        raise ContractError("point IDs must be one-based")
    if len(points) != manifest["point_count"] or [p["row_id"] for p in points] != list(range(1, len(points) + 1)):
        raise ContractError("point IDs must be unique, consecutive, one-based, and complete")
    if Counter(p["year"] for p in points) != {year: POINTS_PER_YEAR for year in YEARS}:
        raise ContractError("point table must contain 512 points for each of 44 years")
    return manifest, points


def diagnostic_quality(diagnostics, numerics):
    """Recheck all entry rounds, including independent labor accounting."""
    periods = diagnostics.get("periods", []) if isinstance(diagnostics, dict) else []
    issues = []
    if not isinstance(periods, list) or any(not isinstance(period, dict) for period in periods):
        periods = []
    if len(periods) != 2:
        issues.append("expected diagnostics for two periods")
    rounds = []
    for period in periods:
        entries = period.get("rounds")
        if not isinstance(entries, list) or not entries or any(not isinstance(item, dict) for item in entries):
            issues.append("missing or malformed round diagnostics")
        else:
            rounds.extend(entries)
    if not rounds:
        issues.append("missing round diagnostics")
    result = {}
    fields = ("root_relative_residual", "max_share_residual", "max_share_stopping_residual",
              "labor_relative_residual", "max_share_iterations")
    for field in fields:
        values = [round_.get(field) for round_ in rounds]
        if not values or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            result[field] = None
            issues.append(f"missing or nonfinite {field}")
        else:
            result[field] = max(abs(v) for v in values)
    caps = {"root_relative_residual": numerics["root_tol"],
            "max_share_residual": numerics["share_tol"],
            "max_share_stopping_residual": numerics["share_tol"],
            "labor_relative_residual": 1e-10}
    for field, cap in caps.items():
        if result[field] is not None and result[field] > cap:
            issues.append(f"{field} exceeds {cap:g}")
    if result["max_share_iterations"] is not None and result["max_share_iterations"] >= numerics["share_max_iter"]:
        issues.append("share iteration cap reached")
    entry_counts = [p.get("entry_iterations") for p in periods]
    result["max_entry_iterations"] = max(entry_counts) if entry_counts and all(isinstance(v, int) for v in entry_counts) else None
    if any(not p.get("entry_stopping_rule_met", False) for p in periods):
        issues.append("entry stopping rule not satisfied")
    if result["max_entry_iterations"] is not None and result["max_entry_iterations"] > numerics["entry_max_iter"]:
        issues.append("entry iteration count exceeds its maximum")
    result["passed"] = not issues
    result["issues"] = issues
    return result


def safe_json_values(value):
    """Keep failed diagnostics serializable; nonfinite numeric fields become null."""
    if isinstance(value, dict):
        return {key: safe_json_values(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [safe_json_values(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def validate_record(record, point, manifest):
    required = {"row_id", "year", "sigma", "N", "M", "zeta", "status", "moments", "phi", "Mbar",
                "elapsed_seconds", "diagnostics", "quality", "error", "run_fingerprint", "point_fingerprint"}
    if not isinstance(record, dict) or not required.issubset(record):
        raise ContractError(f"row {point['row_id']}: missing required record fields")
    elapsed = record["elapsed_seconds"]
    if not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
        raise ContractError(f"row {point['row_id']}: invalid elapsed time")
    if not isinstance(record["diagnostics"], dict) or not isinstance(record["quality"], dict):
        raise ContractError(f"row {point['row_id']}: malformed diagnostics")
    if record.get("run_fingerprint") != manifest["run_fingerprint"]:
        raise ContractError(f"row {point['row_id']}: run fingerprint mismatch")
    if record.get("point_fingerprint") != object_hash(point):
        raise ContractError(f"row {point['row_id']}: point fingerprint mismatch")
    for field in ("row_id", "year", "sigma", "N", "M", "zeta"):
        if record.get(field) != point[field]:
            raise ContractError(f"row {point['row_id']}: mismatched {field}")
    if record.get("status") not in ("ok", "partial", "failed"):
        raise ContractError(f"row {point['row_id']}: invalid status")
    if record["status"] == "ok":
        if not isinstance(record["moments"], dict):
            raise ContractError(f"row {point['row_id']}: missing successful moments")
        values = [record["moments"].get(name) for name in MOMENT_NAMES] + [record.get("phi"), record.get("Mbar")]
        if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            raise ContractError(f"row {point['row_id']}: nonfinite successful output")
        quality = diagnostic_quality(record.get("diagnostics", {}), manifest["numerics"])
        if not quality["passed"] or quality != record.get("quality"):
            raise ContractError(f"row {point['row_id']}: invalid successful diagnostics")


def solve(run_dir, shard_index, shard_count, limit=None):
    """Run one serial shard; an external scheduler supplies parallelism."""
    if shard_count < 1 or not 0 <= shard_index < shard_count or (limit is not None and limit < 1):
        raise ValueError("require shard_count > 0, 0 <= shard_index < shard_count, and limit > 0")
    run_dir = Path(run_dir)
    manifest, points = load_run(run_dir)
    assigned = sorted((p for p in points if (p["row_id"] - 1) % shard_count == shard_index), key=lambda p: (p["M"], p["row_id"]))
    config, numerics = ModelConfig(**manifest["model_config"]), Numerics(**manifest["numerics"])
    draws_cache = OrderedDict()
    counts = Counter({"assigned": len(assigned), "resumed": 0, "solved": 0, "ok": 0, "partial": 0, "failed": 0})
    for point in assigned:
        path = run_dir / "records" / f"{point['row_id']:05d}.json"
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                record = json.load(handle)
            validate_record(record, point, manifest)
            counts["resumed"] += 1
            counts[record["status"]] += 1
            continue
        if limit is not None and counts["solved"] >= limit:
            break
        started = time.perf_counter()
        record = {key: point[key] for key in ("row_id", "year", "sigma", "N", "M", "zeta")}
        record.update(status="failed", moments=None, phi=None, Mbar=None, diagnostics={}, quality={}, error=None,
                      run_fingerprint=manifest["run_fingerprint"], point_fingerprint=object_hash(point))
        try:
            firms = point["M"]
            if firms not in draws_cache:
                draws_cache[firms] = generate_draws(firms, config.markets, seed=manifest["rng"]["seed"])
                if len(draws_cache) > 4:
                    draws_cache.popitem(last=False)
            draws_cache.move_to_end(firms)
            parameters = [FIXED["theta"], FIXED["eta"], FIXED["rho"], point["sigma"], point["N"], point["zeta"]]
            result = simulate(parameters, config=config, numerics=numerics, draws=draws_cache[firms])
            quality = diagnostic_quality(result["diagnostics"], manifest["numerics"])
            moments = {name: float(result["moments"][name]) for name in MOMENT_NAMES}
            phi = float(result["phi"])
            mean_firms = float(np.mean(result["equi"]["Njt"][:, 0]))
            if not np.isfinite([*moments.values(), phi, mean_firms]).all():
                quality["passed"] = False
                quality["issues"].append("nonfinite output moment or statistic")
            record.update(status="ok" if quality["passed"] else "partial", moments=moments,
                          phi=phi, Mbar=mean_firms, diagnostics=result["diagnostics"], quality=quality,
                          error=None if quality["passed"] else "; ".join(quality["issues"]))
            del result
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        record["elapsed_seconds"] = time.perf_counter() - started
        record = safe_json_values(record)
        atomic_write_json(path, record)
        counts["solved"] += 1
        counts[record["status"]] += 1
        print(f"row={point['row_id']} year={point['year']} M={point['M']} status={record['status']} seconds={record['elapsed_seconds']:.3f}", flush=True)
    return dict(counts)


def rank_records(records, target, weights):
    """Return (loss, row ID, record) tuples with deterministic first-row ties."""
    ranked = []
    for record in records:
        if record["status"] != "ok":
            continue
        values = np.asarray([record["moments"][name] for name in MOMENT_NAMES], dtype=np.float64)
        loss = float(np.sum((values - np.asarray(target)) ** 2 * np.asarray(weights)))
        if not math.isfinite(loss):
            raise ContractError(f"nonfinite objective for row {record['row_id']}")
        ranked.append((loss, record["row_id"], record))
    return sorted(ranked, key=lambda item: (item[0], item[1]))


def select(run_dir):
    """Write annual winners and an audit even when a run is incomplete.

    Incomplete or failed searches are conspicuously provisional. The CLI exits
    nonzero in those cases; it never treats missing or invalid solves as zeros.
    """
    run_dir = Path(run_dir)
    manifest, points = load_run(run_dir)
    records, missing, corrupt = [], [], []
    expected_names = {f"{point['row_id']:05d}.json" for point in points}
    extras = sorted(path.name for path in (run_dir / "records").glob("*.json") if path.name not in expected_names)
    for point in points:
        path = run_dir / "records" / f"{point['row_id']:05d}.json"
        if not path.exists():
            missing.append(point["row_id"])
            continue
        try:
            with path.open(encoding="utf-8") as handle:
                record = json.load(handle)
            validate_record(record, point, manifest)
            records.append(record)
        except (ContractError, ValueError, KeyError, TypeError) as exc:
            corrupt.append({"row_id": point["row_id"], "year": point["year"], "error": str(exc)})
    failed = [{"row_id": record["row_id"], "year": record["year"], "status": record["status"], "error": record["error"]}
              for record in records if record["status"] != "ok"]
    complete = len(records) == len(points) and not (missing or corrupt or extras)
    provisional = not complete or bool(failed)
    annual, top_rows = [], []
    for year in YEARS:
        year_records = [record for record in records if record["year"] == year]
        ranked = rank_records(year_records, manifest["targets"][str(year)], manifest["weights"])
        row = {"year": year, "n_expected": POINTS_PER_YEAR, "n_completed": len(year_records),
               "n_valid": len(ranked), "n_failed": len(year_records) - len(ranked), "provisional": provisional}
        if ranked:
            loss, row_id, best = ranked[0]
            row.update(row_id=row_id, loss=loss, n_top15=min(15, len(ranked)))
            for key in ("sigma", "N", "M", "zeta", "phi", "Mbar"):
                row[key] = best[key]
            row["mean_active_firms"] = best["Mbar"]
            row.update(best["moments"])
            if len(ranked) > 1:
                row.update(runner_up_row_id=ranked[1][1], runner_up_loss=ranked[1][0],
                           runner_up_gap=ranked[1][0] - loss,
                           runner_up_relative_gap=(ranked[1][0] - loss) / abs(loss) if loss else None)
            box = manifest["boxes"][str(year)]
            for parameter in PARAMETERS:
                row[f"{parameter}_pos"] = (best[parameter] - box[f"{parameter}_lo"]) / (box[f"{parameter}_hi"] - box[f"{parameter}_lo"])
                row[f"{parameter}_top15_lo"] = min(item[2][parameter] for item in ranked[:15])
                row[f"{parameter}_top15_hi"] = max(item[2][parameter] for item in ranked[:15])
            row["boundary_10pct"] = any(row[f"{p}_pos"] < .1 or row[f"{p}_pos"] > .9 for p in PARAMETERS)
            row.update(REALL=best["moments"][MOMENT_NAMES[0]], mu_w=best["moments"][MOMENT_NAMES[1]], sga_tc=best["moments"][MOMENT_NAMES[2]])
            for rank, (candidate_loss, _, candidate) in enumerate(ranked[:15], start=1):
                top = {"year": year, "rank": rank, "loss": candidate_loss}
                top.update({key: candidate[key] for key in ("row_id", "sigma", "N", "M", "zeta", "phi", "Mbar")})
                top.update(candidate["moments"])
                top_rows.append(top)
        target = manifest["targets"][str(year)]
        row.update({f"target_{name}": value for name, value in zip(MOMENT_NAMES, target)})
        row.update(REALL_data=target[0], mu_data=target[1], sga_data=target[2])
        annual.append(row)
    fields = ["year", "row_id", "n_expected", "n_completed", "n_valid", "n_failed", "provisional", "loss",
              "runner_up_row_id", "runner_up_loss", "runner_up_gap", "runner_up_relative_gap",
              "sigma", "N", "M", "zeta", "phi", "Mbar", "mean_active_firms", *MOMENT_NAMES,
              "REALL", "mu_w", "sga_tc", *(f"target_{name}" for name in MOMENT_NAMES), "REALL_data", "mu_data", "sga_data",
              *(f"{parameter}_{suffix}" for parameter in PARAMETERS for suffix in ("pos", "top15_lo", "top15_hi")),
              "n_top15", "boundary_10pct"]
    atomic_write_bytes(run_dir / "annual_estimates.csv", csv_bytes(annual, fields))
    atomic_write_bytes(run_dir / "top15.csv", csv_bytes(top_rows, ["year", "rank", "row_id", "sigma", "N", "M", "zeta", "loss", "phi", "Mbar", *MOMENT_NAMES]))
    summary = {"schema_version": SCHEMA_VERSION, "created_utc": datetime.now(timezone.utc).isoformat(),
               "run_fingerprint": manifest["run_fingerprint"], "expected_records": len(points), "completed_records": len(records),
               "missing_records": missing, "failed_records": failed, "corrupt_records": corrupt, "unexpected_record_files": extras,
               "status_counts": dict(Counter(record["status"] for record in records)),
               "complete": complete, "provisional": provisional, "selection_valid": complete and not failed,
               "years_with_winners": sum("row_id" in row for row in annual),
               "years_with_boundary_winners": sum(bool(row.get("boundary_10pct")) for row in annual),
               "weights": manifest["weights"], "weight_variance_ddof": 1,
               "total_candidate_seconds": sum(record.get("elapsed_seconds", 0) for record in records),
               "total_selected_loss": sum(row["loss"] for row in annual if "loss" in row),
               "interpretation": "Best of 512 specified candidates per year; no continuous-global-optimum claim."}
    for source, destination in (("root_relative_residual", "max_root_relative_residual"),
                                ("max_share_residual", "max_share_residual"),
                                ("max_share_stopping_residual", "max_share_stopping_residual"),
                                ("labor_relative_residual", "max_labor_relative_residual"),
                                ("max_share_iterations", "max_share_iterations"),
                                ("max_entry_iterations", "max_entry_iterations")):
        values = [record.get("quality", {}).get(source) for record in records]
        values = [value for value in values if isinstance(value, (int, float)) and math.isfinite(value)]
        summary[destination] = max(values) if values else None
    atomic_write_json(run_dir / "summary.json", summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="freeze 44 × 512 candidates and run contract")
    prepare_parser.add_argument("--data-dir", type=Path, required=True)
    prepare_parser.add_argument("--run-dir", type=Path, required=True)
    solve_parser = commands.add_parser("solve", help="solve one serial shard, resuming atomic row checkpoints")
    solve_parser.add_argument("--run-dir", type=Path, required=True)
    solve_parser.add_argument("--shard-index", type=int, required=True)
    solve_parser.add_argument("--shard-count", type=int, required=True)
    solve_parser.add_argument("--limit", type=int, help="maximum new solves in a smoke run; never marks the full run complete")
    select_parser = commands.add_parser("select", help="select annual candidates and audit completeness")
    select_parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            manifest = prepare(args.data_dir, args.run_dir)
            print(json.dumps({"point_count": manifest["point_count"], "run_fingerprint": manifest["run_fingerprint"]}))
        elif args.command == "solve":
            summary = solve(args.run_dir, args.shard_index, args.shard_count, args.limit)
            print(json.dumps(summary, sort_keys=True))
            return 2 if summary["failed"] or summary["partial"] else 0
        else:
            summary = select(args.run_dir)
            print(json.dumps({key: summary[key] for key in ("expected_records", "completed_records", "status_counts", "complete", "provisional", "selection_valid")}, sort_keys=True))
            return 0 if summary["selection_valid"] else 2
    except (ContractError, OSError, ValueError, KeyError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
