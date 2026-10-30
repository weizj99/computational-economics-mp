"""Export actual fixed-parameter economy solves for an offline teaching page.

The observer reads the real frozen solver's local arrays at its existing
iteration boundaries. It neither reimplements the share algorithm nor changes
any solver local variable.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import inspect
import html
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import traceback
from types import SimpleNamespace
import zipfile

import numpy as np
import scipy


SOURCE_FILES = ("__init__.py", "draws.py", "equilibrium.py", "moments.py")
MOMENTS = ("employment_reallocation_rate", "markup_sales_weighted", "sga_cost_share_sales_weighted")
ATOL = 1e-12


class ContractError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def object_hash(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_hash(value):
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256(canonical({"shape": array.shape, "dtype": array.dtype.str}).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def safe_json(value):
    if isinstance(value, dict):
        return {str(k): safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return safe_json(value.tolist())
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_bytes(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("xb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def atomic_json(path, value):
    atomic_bytes(path, (json.dumps(safe_json(value), sort_keys=True, indent=2, allow_nan=False) + "\n").encode())


def freeze(source, destination):
    source, destination = Path(source), Path(destination)
    content = source.read_bytes()
    if destination.exists():
        require(destination.read_bytes() == content, f"frozen destination differs: {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(content)


def runtime_versions():
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}


def import_qmp(directory):
    directory = Path(directory).resolve()
    sys.dont_write_bytecode = True
    existing = sys.modules.get("qmp")
    require(existing is None or Path(existing.__file__).resolve().parent == directory / "qmp",
            "a different qmp source tree is already imported")
    sys.path.insert(0, str(directory))
    validation = SimpleNamespace(source_hashes=lambda: {name: file_hash(directory / "qmp" / name) for name in SOURCE_FILES},
                                 diagnostic_quality=diagnostic_quality)
    return (importlib.import_module("qmp"), validation,
            importlib.import_module("qmp.equilibrium"), importlib.import_module("qmp.draws"))


def diagnostic_quality(diagnostics, numerics):
    """The same all-round acceptance gates as the validated production search."""
    issues = []
    periods = diagnostics.get("periods", [])
    if len(periods) != 2:
        issues.append("expected two periods")
    rounds = [r for p in periods for r in p.get("rounds", [])]
    if not rounds or any(not p.get("rounds") for p in periods):
        issues.append("missing all-round diagnostics")
    quality = {}
    caps = {"root_relative_residual": numerics["root_tol"], "max_share_residual": numerics["share_tol"],
            "max_share_stopping_residual": numerics["share_tol"], "labor_relative_residual": 1e-10}
    for field in (*caps, "max_share_iterations"):
        values = [r.get(field) for r in rounds]
        if not values or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            quality[field] = None
            issues.append(f"nonfinite/missing {field}")
        else:
            quality[field] = max(abs(v) for v in values)
            if field in caps and quality[field] > caps[field]:
                issues.append(f"{field} exceeds common tolerance")
    if quality.get("max_share_iterations") is not None and quality["max_share_iterations"] >= numerics["share_max_iter"]:
        issues.append("share cap reached")
    quality["max_entry_iterations"] = max((p.get("entry_iterations", 0) for p in periods), default=0)
    if any(not p.get("entry_stopping_rule_met", False) for p in periods):
        issues.append("entry stopping rule not satisfied")
    if quality["max_entry_iterations"] > numerics["entry_max_iter"]:
        issues.append("entry count exceeds cap")
    quality.update(passed=not issues, issues=issues)
    return quality


def teaching_draws(qmp, firms, markets, seed):
    bank = qmp.generate_draws(18, markets, seed=seed)
    require(1 <= firms <= 18, "teaching bank supports M up to 18")
    return {name: value[:firms, :] for name, value in bank.items()}


def initial_anchor(x, config, numerics, draws, equilibrium, draw_module):
    x = np.asarray(x, dtype=np.float64)
    productivity, u, _ = draw_module.build_productivity(x, config.markets, config.zbar, draws)
    z = productivity[:, :, 0]
    active = z > 0
    counts = active.sum(axis=0)
    s, mu, _ = equilibrium.solve_shares(z, x[0], x[1], config.gamma, numerics)
    wc, _, demand, sum_part = equilibrium._prices(z, active, s, mu, counts, int(np.count_nonzero(counts)), x[0], x[1], config)
    return anchor_from_initial_state({"z": z, "u": u, "active": active, "mu": mu, "demand": demand,
                                      "wc": wc, "sum_part": sum_part, "c": config, "zeta": x[5]}, equilibrium)


def build_design(input_dir, qmp, equilibrium, draw_module):
    with (Path(input_dir) / "boxes.csv").open(newline="", encoding="utf-8-sig") as stream:
        box = next(row for row in csv.DictReader(stream) if int(row["year"]) == 2000)
    # The baseline is the centre of the year-2000 search box, to six decimals.
    baseline_values = [round((float(box[f"{name}_lo"]) + float(box[f"{name}_hi"])) / 2, 6)
                       for name in ("sigma", "N", "zeta")]
    require(baseline_values == [.047041, 14.222682, .919212], "the year-2000 box centre differs")
    with (Path(input_dir) / "Moments.csv").open(newline="", encoding="utf-8-sig") as stream:
        data = list(csv.DictReader(stream))
    require([int(row["year"]) for row in data] == list(range(1980, 2024)), "expected unchanged 44-year target table")
    columns = ("rer_total", "mu_w", "mean_sga_tc_w")
    matrix = np.array([[float(row[name]) for name in columns] for row in data])
    weights = dict(zip(MOMENTS, (1 / matrix.var(axis=0, ddof=1)).tolist()))
    target = dict(zip(MOMENTS, matrix[20].tolist()))
    baseline_x = [1.13125, 4.36875, .9, *baseline_values]
    config, numerics = qmp.ModelConfig(), qmp.Numerics()
    path_specs = {
        "sigma": ("Productivity dispersion", 3, [.032, .0395, .047041, .0545, .062]),
        "entrants": ("Potential entrants", 4, [10., 12., 14.222682, 16., 18.]),
        "overhead": ("Overhead setting", 5, [.70, .80, .919212, .97, 1.03]),
        "seed": ("Simulation seed", None, [100, 101, 102, 103, 104]),
    }
    base_key = (tuple(baseline_x), 100)
    point_map = {base_key: {"id": "baseline", "x": baseline_x, "seed": 100}}
    paths = {}
    for path_id, (label, position, levels) in path_specs.items():
        points = []
        for index, value in enumerate(levels):
            x, seed = baseline_x.copy(), 100
            if position is None:
                seed = int(value)
            else:
                x[position] = value
            key = (tuple(x), seed)
            if key not in point_map:
                point_map[key] = {"id": f"{path_id}_{index}", "x": x, "seed": seed}
            case_id = point_map[key]["id"]
            text = f"seed {seed}" if position is None else (f"σ = {value:.6f}" if position == 3 else f"N = {value:g}" if position == 4 else f"ζ = {value:.6f}")
            points.append({"case_id": case_id, "label": text})
        paths[path_id] = {"label": label, "points": points, "default_point": 0 if path_id == "seed" else 2}
    require(len(point_map) == 17, "expected 17 distinct parameter/seed points")
    references = {}
    for point in point_map.values():
        key = object_hash(point["x"])
        if key not in references:
            donors = []
            for seed in (500, 501, 502):
                draws = teaching_draws(qmp, math.floor(point["x"][4]), config.markets, seed)
                anchor = initial_anchor(point["x"], config, numerics, draws, equilibrium, draw_module)
                donors.append({"seed": seed, "anchor": anchor})
            references[key] = {"x": point["x"], "phi": float(np.median([d["anchor"]["natural_phi"] for d in donors])),
                               "donors": donors, "rule": "median_of_three_separate_original_H_values"}
    base_phi = references[object_hash(baseline_x)]["phi"]
    overhead_ids = {p["case_id"] for p in paths["overhead"]["points"]}
    scenarios = []
    for point in point_map.values():
        ref_phi = references[object_hash(point["x"])]["phi"]
        for mode in ("sample", "reference", "direct"):
            phi = None if mode == "sample" else (ref_phi if mode == "reference" or point["id"] in overhead_ids else base_phi)
            scenarios.append({"id": f"{point['id']}_{mode}", "case_id": point["id"], "mode": mode,
                              "x": point["x"], "seed": point["seed"],
                              "phi_rule": "natural" if mode == "sample" else "given", "phi_value": phi})
    return {"title": "One economy, five steps", "config": asdict(config), "numerics": asdict(numerics),
            "market_index": 0, "baseline_id": "baseline_sample", "scenarios": scenarios,
            "paths": paths, "points": list(point_map.values()), "reference_anchors": references,
            "reference_base_phi": base_phi, "target_year": 2000, "target": target, "weights": weights,
            "draw_contract": "New teaching experiment: generate_draws(18,10000,seed), then keep first M rows of each firm shock array. Sector shocks remain unchanged. Nested common shocks across N; seed labels do not reproduce the annual estimator's M-specific draw stream.",
            "anchor_contract": "sample uses H(sigma,N,zeta;eval draw). reference uses the median of three separately computed H values at independent reference seeds 500,501,502. No pooling of shocks or Gamma before taking maxima. direct holds the baseline reference phi fixed except on the overhead path, where it deliberately matches the point's reference phi."}


def source_line(function, exact_text):
    lines, first = inspect.getsourcelines(function)
    matches = [first + index for index, line in enumerate(lines) if line.strip() == exact_text]
    require(len(matches) == 1, f"frozen trace boundary is absent or ambiguous: {exact_text}")
    return matches[0]


def anchor_from_initial_state(local, equilibrium):
    """Read-only closed-form anchor diagnostic, using original first-round state."""
    z, u, active = local["z"], local["u"], local["active"]
    mu, demand, wc, sum_part, c, zeta = (local[k] for k in ("mu", "demand", "wc", "sum_part", "c", "zeta"))
    power = equilibrium._power
    demand_power = power(demand, 1 / c.gamma, active)
    numerator = (mu - c.gamma) * c.varphibar * wc ** (c.varphi / c.alpha_cogs) * demand_power
    denominator = (c.alpha_cogs * c.psi_cogs * u * power(z, 1 / c.gamma, active) / c.psi_sga * sum_part
                   + (mu - c.gamma) * demand_power * equilibrium._sum_firms(u))
    values = np.sort(numerator[active] / denominator[active])
    if zeta < 1:
        cdf = np.cumsum(np.full(values.size, 1 / values.size))
        index = int(np.searchsorted(cdf, zeta, side="right"))
        require(index < values.size, "overhead quantile has no support")
        natural_phi = float(values[index])
        rule = "strict_empirical_quantile"
    else:
        natural_phi = float(zeta * values[-1])
        rule = "zeta_times_max_Gamma"
    return {"natural_phi": natural_phi, "rule": rule, "zeta": float(zeta), "count": int(values.size),
            "Gamma_min": float(values[0]), "Gamma_median": float(np.median(values)),
            "Gamma_q95": float(np.quantile(values, .95)), "Gamma_q99": float(np.quantile(values, .99)),
            "Gamma_q999": float(np.quantile(values, .999)), "Gamma_max": float(values[-1]),
            "Gamma_second_max": float(values[-2]) if values.size > 1 else None}


class SolverObserver:
    """Read actual iteration states, without altering source or local variables."""

    def __init__(self, equilibrium, market_index):
        self.eq = equilibrium
        self.market = market_index
        self.period_code = equilibrium._solve_period.__code__
        self.share_code = equilibrium.solve_shares.__code__
        self.share_initial_line = source_line(equilibrium.solve_shares, "z_inverse = _power(z, -1 / gamma, active)")
        self.share_after_line = source_line(equilibrium.solve_shares, "done |= working & (distance < n.share_tol)")
        self.period_anchor_line = source_line(equilibrium._solve_period, "fixed_labor = phi * u")
        self.period_round_line = source_line(equilibrium._solve_period, "round_records.append(record)")
        self.period_frames = {}
        self.share_frames = {}
        self.periods = []
        self.anchor = None

    def __enter__(self):
        require(sys.gettrace() is None, "a debugger/trace callback is already active")
        sys.settrace(self.global_trace)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        sys.settrace(None)
        return False

    def global_trace(self, frame, event, arg):
        if event != "call":
            return None
        if frame.f_code is self.period_code:
            period = {"period": len(self.periods), "rounds": [], "share_calls": []}
            self.periods.append(period)
            self.period_frames[id(frame)] = period
            return self.period_trace
        if frame.f_code is self.share_code and id(frame.f_back) in self.period_frames:
            parent = self.period_frames[id(frame.f_back)]
            call = {"entry_round": int(frame.f_back.f_locals["iteration"]), "steps": []}
            parent["share_calls"].append(call)
            self.share_frames[id(frame)] = call
            return self.share_trace
        return None

    def share_trace(self, frame, event, arg):
        local, call, j = frame.f_locals, self.share_frames[id(frame)], self.market
        if event == "line" and frame.f_lineno == self.share_initial_line:
            call.update(z=local["z"][:, j].copy().tolist(), initial_share=local["s"][:, j].copy().tolist(),
                        active=local["active"][:, j].copy().tolist(), active_firms=int(local["count"][j]))
        elif event == "line" and frame.f_lineno == self.share_after_line:
            if local["working"][j] and call["entry_round"] == 1:
                call["steps"].append({"iteration": int(local["iteration"]),
                                      "share": local["s"][:, j].copy().tolist(),
                                      "proposed_share": local["proposed"][:, j].copy().tolist(),
                                      "markup": local["mu"][:, j].copy().tolist(),
                                      "relative_residual": float(local["distance"][j]),
                                      "meets_stopping_tolerance": bool(local["distance"][j] < local["n"].share_tol)})
        elif event == "return":
            if arg is not None:
                s, mu, diagnostic = arg
                call.update(final_share=s[:, j].copy().tolist(), final_markup=mu[:, j].copy().tolist(),
                            iterations=int(diagnostic["iterations"][j]),
                            stopping_residual=float(diagnostic["stopping_residual"][j]),
                            returned_residual=float(diagnostic["returned_residual"][j]))
            self.share_frames.pop(id(frame), None)
        return self.share_trace

    def period_trace(self, frame, event, arg):
        local, period, j = frame.f_locals, self.period_frames[id(frame)], self.market
        if event == "line" and frame.f_lineno == self.period_anchor_line and self.anchor is None:
            self.anchor = anchor_from_initial_state(local, self.eq)
        elif event == "line" and frame.f_lineno == self.period_round_line:
            stopping = local["dropped"] < local["n"].entry_drop_stop or local["iteration"] == local["n"].entry_max_iter
            market = {"z": local["z"][:, j].copy().tolist(), "share": local["s"][:, j].copy().tolist(),
                      "markup": local["mu"][:, j].copy().tolist(), "active": local["active"][:, j].copy().tolist(),
                      "profit": local["profits"][:, j].copy().tolist(),
                      "production_labor": local["labor"][:, j].copy().tolist(),
                      "fixed_labor": local["fixed_labor"][:, j].copy().tolist(),
                      "proposed_drop": local["drop"][:, j].copy().tolist()}
            period["rounds"].append({**local["record"], "selected_market": market,
                                     "profit_threshold": float(local["threshold"]),
                                     "deletion_applied": not stopping,
                                     "actual_drop": 0 if stopping else int(local["dropped"]),
                                     "phi": float(local["phi"]), "wage": float(local["wage"]),
                                     "output": float(local["output"]), "labor_supply": float(local["supply"]),
                                     "production_labor": float(local["actual_production"]),
                                     "fixed_labor": float(local["overhead"])})
        elif event == "return":
            if arg is not None:
                period["stop_reason"] = arg[3]["entry_stop_reason"]
                period["entry_iterations"] = int(arg[3]["entry_iterations"])
            self.period_frames.pop(id(frame), None)
        return self.period_trace


def solve_with_phi(x, config, numerics, draws, phi, qmp, equilibrium, draw_module):
    """Assemble two original period solves with an explicit common phi."""
    parameters = np.asarray(x, dtype=np.float64)
    equilibrium._validate(parameters, config, numerics)
    productivity, overhead, source = draw_module.build_productivity(parameters, config.markets, config.zbar, draws)
    periods, diagnostics = [], []
    for t in range(2):
        period, returned_phi, err, diagnosis = equilibrium._solve_period(
            productivity[:, :, t], overhead, parameters[0], parameters[1], parameters[5], config, numerics, phi)
        require(returned_phi == phi, "supplied phi changed")
        periods.append(period)
        diagnostics.append(diagnosis)
    equi = {f"{key}_ijt": np.stack([p[key] for p in periods], axis=2)
            for key in ("phi", "mu", "z", "s", "y", "p", "u", "n")}
    equi.update({f"{key}_t": np.array([p[key] for p in periods]) for key in ("W", "Y", "Ns", "Nprod")})
    equi["Njt"] = np.stack([p["Njt"] for p in periods], axis=1)
    equi["share_iterations"] = np.stack([p["share_iterations"] for p in periods], axis=1)
    return {"equi": equi, "phi": phi, "err": err,
            "moments": qmp.compute_moments(equi, gamma=config.gamma, alpha_cogs=config.alpha_cogs,
                                           psi_cogs=config.psi_cogs, psi_sga=config.psi_sga),
            "diagnostics": {"dtype": "float64", "draw_source": source, "config": asdict(config),
                            "numerics": asdict(numerics), "periods": diagnostics,
                            "entry_method": "sequential_exit_pre_exit_stop_no_reentry_test",
                            "entry_stopping_rule_met": all(p["entry_stopping_rule_met"] for p in diagnostics)}}


def exact_comparison(reference, observed):
    differences = {name: abs(reference["moments"][name] - observed["moments"][name]) for name in MOMENTS}
    differences["phi"] = abs(reference["phi"] - observed["phi"])
    hashes = {key: array_hash(reference["equi"][key]) == array_hash(observed["equi"][key]) for key in reference["equi"]}
    fields = ("iteration", "active_firms", "active_markets", "loss_firms", "proposed_drop")
    history = lambda result: [{"stop_reason": p["entry_stop_reason"], "rounds": [{key: r[key] for key in fields} for r in p["rounds"]]}
                              for p in result["diagnostics"]["periods"]]
    same_history = history(reference) == history(observed)
    return {"passed": same_history and all(hashes.values()) and all(v <= ATOL for v in differences.values()),
            "absolute_differences": differences, "equilibrium_array_hash_equal": hashes,
            "entry_history_equal": same_history,
            "absolute_tolerance": ATOL, "relative_tolerance": 0.0}


def public_result(result, observer, scenario, market_index):
    e = result["equi"]
    production, fixed = e["n_ijt"], e["phi_ijt"]
    active = production > 0
    employment = np.where(active, production + fixed, 0.0)
    denominator = float(.5 * employment.sum())
    changes = np.abs(employment[:, :, 1] - employment[:, :, 0])
    masks = {"continuing": active[:, :, 0] & active[:, :, 1],
             "entrant": ~active[:, :, 0] & active[:, :, 1], "exiting": active[:, :, 0] & ~active[:, :, 1]}
    flow = {name: {"count": int(mask.sum()), "contribution": float(changes[mask].sum() / denominator)}
            for name, mask in masks.items()}
    reconstructed = sum(item["contribution"] for item in flow.values())
    require(abs(reconstructed - result["moments"][MOMENTS[0]]) <= ATOL, "reallocation flow identity failed")
    periods = []
    for t in range(2):
        periods.append({"period": t, "active_firms": int(active[:, :, t].sum()),
                        "active_markets": int(np.count_nonzero(e["Njt"][:, t])),
                        "mean_active_firms": float(e["Njt"][:, t].mean()),
                        "production_labor": float(production[:, :, t].sum()),
                        "fixed_labor": float(np.where(active[:, :, t], fixed[:, :, t], 0).sum()),
                        "total_employment": float(employment[:, :, t].sum()),
                        "output": float(e["Y_t"][t]), "wage": float(e["W_t"][t]),
                        "market_employment": employment[:, market_index, t].tolist()})
    return {"id": scenario["id"], "case_id": scenario.get("case_id", scenario["id"]), "mode": scenario.get("mode", "sample"),
            "params": scenario["x"], "seed": scenario["seed"],
            "phi_rule": scenario["phi_rule"], "phi": float(result["phi"]),
            "M": int(np.floor(scenario["x"][4])), "market_index": market_index,
            "anchor": observer.anchor, "moments": result["moments"], "period_totals": periods,
            "flows": flow, "flow_reconstruction_error": abs(reconstructed - result["moments"][MOMENTS[0]]),
            "period_trace": observer.periods,
            "final_market": {key: e[f"{key}_ijt"][:, market_index, :].tolist()
                             for key in ("z", "s", "mu", "n", "phi")}}


def validate_design(design, qmp):
    config = qmp.ModelConfig(**design["config"])
    numerics = qmp.Numerics(**design["numerics"])
    require(config.markets == 10000, "teaching export must retain J=10000")
    require(asdict(numerics) == asdict(qmp.Numerics()), "retain the validated common numerical tolerances")
    require(0 <= design["market_index"] < config.markets, "selected market is outside the economy")
    ids = set()
    for case in design["scenarios"]:
        require(isinstance(case["id"], str) and case["id"] not in ids
                and all(ch.isalnum() or ch in "_-" for ch in case["id"]), "scenario IDs must be unique safe names")
        ids.add(case["id"])
        require(len(case["x"]) == 10 and np.isfinite(case["x"]).all(), "scenario must specify ten finite parameters")
        require(case["phi_rule"] in ("natural", "baseline_fixed", "given"), "unknown phi rule")
        require(isinstance(case["seed"], int) and case["seed"] >= 0, "seed must be a nonnegative integer")
        if case["phi_rule"] == "given":
            require(math.isfinite(case["phi_value"]) and case["phi_value"] >= 0, "given phi must be nonnegative finite")
    require(design["baseline_id"] in ids, "baseline is absent")
    baseline = next(c for c in design["scenarios"] if c["id"] == design["baseline_id"])
    require(baseline["phi_rule"] == "natural", "baseline must use natural phi")
    return config, numerics, baseline


def prepare(source_python, input_dir, run_dir):
    source_python, run_dir = Path(source_python).resolve(), Path(run_dir).resolve()
    require(source_python != run_dir and source_python not in run_dir.parents, "use a new run outside the source tree")
    if (run_dir / "manifest.json").exists():
        return load_run(run_dir)[0]
    require(not (run_dir / "records").exists() or not any((run_dir / "records").iterdir()), "records exist without manifest")
    for name in SOURCE_FILES:
        freeze(source_python / "qmp" / name, run_dir / "frozen_python/qmp" / name)
    freeze(Path(__file__).resolve(), run_dir / "economy_export.py")
    for name in ("Moments.csv", "boxes.csv"):
        freeze(Path(input_dir) / name, run_dir / "inputs" / name)
    freeze(run_dir / "anchor_definition_check.json", run_dir / "inputs/anchor_definition_check.json")
    qmp, estimation, equilibrium, draw_module = import_qmp(run_dir / "frozen_python")
    design = build_design(run_dir / "inputs", qmp, equilibrium, draw_module)
    atomic_json(run_dir / "design.json", design)
    config, numerics, baseline = validate_design(design, qmp)
    draws = teaching_draws(qmp, int(np.floor(baseline["x"][4])), config.markets, baseline["seed"])
    reference = qmp.simulate(baseline["x"], config=config, numerics=numerics, draws=draws)
    quality = estimation.diagnostic_quality(reference["diagnostics"], asdict(numerics))
    require(quality["passed"], "baseline solver diagnostics failed")
    with SolverObserver(equilibrium, design["market_index"]) as observer:
        observed = qmp.simulate(baseline["x"], config=config, numerics=numerics, draws=draws)
    instrument_check = exact_comparison(reference, observed)
    require(instrument_check["passed"], "read-only instrumentation changed the baseline")
    with SolverObserver(equilibrium, design["market_index"]) as fixed_observer:
        fixed = solve_with_phi(baseline["x"], config, numerics, draws, reference["phi"], qmp, equilibrium, draw_module)
    fixed_check = exact_comparison(reference, fixed)
    require(fixed_check["passed"], "explicit-phi assembly does not reproduce the baseline")
    require(len(observer.periods) == 2 and all(len(p["rounds"]) == reference["diagnostics"]["periods"][t]["entry_iterations"]
            for t, p in enumerate(observer.periods)), "observer missed actual solver rounds")
    require(abs(observer.anchor["natural_phi"] - reference["phi"]) <= ATOL, "anchor diagnostic differs")
    high_zeta = next(case for case in design["scenarios"] if case["mode"] == "sample" and case["x"][5] >= 1)
    high_draws = teaching_draws(qmp, math.floor(high_zeta["x"][4]), config.markets, high_zeta["seed"])
    high_reference = qmp.simulate(high_zeta["x"], config=config, numerics=numerics, draws=high_draws)
    with SolverObserver(equilibrium, design["market_index"]) as high_observer:
        high_observed = qmp.simulate(high_zeta["x"], config=config, numerics=numerics, draws=high_draws)
    high_check = exact_comparison(high_reference, high_observed)
    require(high_check["passed"] and high_observer.anchor["rule"] == "zeta_times_max_Gamma", "max-Gamma branch instrumentation failed")
    require(estimation.diagnostic_quality(high_observed["diagnostics"], asdict(numerics))["passed"], "max-Gamma scenario diagnostic failed")
    require(abs(high_observer.anchor["natural_phi"] - high_observed["phi"]) <= ATOL, "max-Gamma formula differs")
    verification = {"passed": True, "instrumentation": instrument_check, "explicit_phi": fixed_check,
                    "max_Gamma_branch_instrumentation": high_check,
                    "baseline_quality": quality, "baseline_moments": reference["moments"],
                    "baseline_phi": float(reference["phi"]),
                    "source_sha256": estimation.source_hashes(), "runtime_versions": runtime_versions()}
    atomic_json(run_dir / "baseline_verification.json", verification)
    atomic_json(run_dir / "baseline_observed.json", public_result(observed, observer, baseline, design["market_index"]))
    manifest = {"schema_version": 1, "experiment": "unit02_fixed_parameter_economies",
                "created_utc": datetime.now(timezone.utc).isoformat(), "title": design.get("title", "One economy"),
                "scenario_count": len(design["scenarios"]), "baseline_id": design["baseline_id"],
                "baseline_phi": float(reference["phi"]), "market_index": design["market_index"],
                "reference_base_phi": design["reference_base_phi"],
                "model_config": asdict(config), "numerics": asdict(numerics), "moment_names": list(MOMENTS),
                "source_sha256": estimation.source_hashes(), "runtime_versions": runtime_versions(),
                "driver_sha256": file_hash(run_dir / "economy_export.py"),
                "input_sha256": {name: file_hash(run_dir / name) for name in
                                 ("design.json", "baseline_verification.json", "baseline_observed.json", "inputs/Moments.csv", "inputs/boxes.csv", "inputs/anchor_definition_check.json")},
                "contract": "Fixed-parameter scenarios, no estimation. All solves retain J=10000, two periods and the common numerical precision. Natural phi follows the original rule; a fixed or explicitly given phi is a labelled intervention. Browser controls select precomputed solves; no interpolated equilibrium is represented as solved.",
                "matched_paths": "Reference and direct modes coincide by construction on the seed and overhead paths. The sigma and entrants paths compare re-calibration with an explicitly fixed cost. Equality on a matched path is not evidence of general equivalence.",
                "observer": "Read-only Python tracing of the frozen solve_shares and _solve_period. Every trace step is an actual state of that solve. No local frame mutation or alternative share algorithm."}
    manifest["run_fingerprint"] = object_hash(manifest)
    (run_dir / "records").mkdir(parents=True, exist_ok=True)
    atomic_json(run_dir / "manifest.json", manifest)
    return manifest


def load_run(run_dir):
    run_dir = Path(run_dir).resolve()
    manifest = read_json(run_dir / "manifest.json")
    require(manifest["run_fingerprint"] == object_hash({k: v for k, v in manifest.items() if k != "run_fingerprint"}), "manifest hash differs")
    require(manifest["schema_version"] == 1 and manifest["runtime_versions"] == runtime_versions(), "schema/runtime differs")
    require(file_hash(Path(__file__)) == manifest["driver_sha256"] and file_hash(run_dir / "economy_export.py") == manifest["driver_sha256"], "driver differs")
    for name, digest in manifest["source_sha256"].items():
        require(file_hash(run_dir / "frozen_python/qmp" / name) == digest, f"solver source differs: {name}")
    for name, digest in manifest["input_sha256"].items():
        require(file_hash(run_dir / name) == digest, f"frozen input differs: {name}")
    design = read_json(run_dir / "design.json")
    require(len(design["scenarios"]) == manifest["scenario_count"], "scenario count differs")
    return manifest, design


def validate_record(record, case, manifest, estimation):
    require(record["id"] == case["id"] and record["scenario_fingerprint"] == object_hash(case), "scenario identity differs")
    require(record["run_fingerprint"] == manifest["run_fingerprint"], "record run differs")
    require(record["status"] in ("ok", "invalid", "failed"), "unknown status")
    if record["status"] == "ok":
        require(record["quality"]["passed"] and estimation.diagnostic_quality(record["diagnostics"], manifest["numerics"])["passed"], "successful diagnostics invalid")
        require(all(math.isfinite(record["result"]["moments"][name]) for name in MOMENTS), "nonfinite successful moments")
        require(record["anchor_check"]["passed"], "successful anchor check failed")


def solve(run_dir, shard_index=0, shard_count=1, limit=None):
    require(shard_count > 0 and 0 <= shard_index < shard_count, "invalid shard specification")
    run_dir = Path(run_dir).resolve()
    manifest, design = load_run(run_dir)
    qmp, estimation, equilibrium, draw_module = import_qmp(run_dir / "frozen_python")
    config, numerics, _ = validate_design(design, qmp)
    assigned = [case for index, case in enumerate(design["scenarios"]) if index % shard_count == shard_index]
    counts = Counter(assigned=len(assigned), cached=0, solved=0, ok=0, invalid=0, failed=0)
    for case in assigned:
        path = run_dir / "records" / f"{case['id']}.json"
        if path.exists():
            saved = read_json(path)
            validate_record(saved, case, manifest, estimation)
            counts["cached"] += 1
            counts[saved["status"]] += 1
            continue
        if limit is not None and counts["solved"] >= limit:
            break
        started = time.perf_counter()
        record = {"id": case["id"], "status": "failed", "error": None,
                  "run_fingerprint": manifest["run_fingerprint"], "scenario_fingerprint": object_hash(case),
                  "quality": {}, "diagnostics": {}, "result": None, "anchor_check": {}}
        try:
            draws = teaching_draws(qmp, int(np.floor(case["x"][4])), config.markets, case["seed"])
            phi = None if case["phi_rule"] == "natural" else (manifest["baseline_phi"] if case["phi_rule"] == "baseline_fixed" else case["phi_value"])
            with SolverObserver(equilibrium, design["market_index"]) as observer:
                result = (qmp.simulate(case["x"], config=config, numerics=numerics, draws=draws) if phi is None
                          else solve_with_phi(case["x"], config, numerics, draws, phi, qmp, equilibrium, draw_module))
            quality = estimation.diagnostic_quality(result["diagnostics"], manifest["numerics"])
            expected_phi = observer.anchor["natural_phi"] if phi is None else phi
            anchor_difference = abs(float(result["phi"]) - expected_phi)
            anchor_check = {"passed": anchor_difference <= ATOL, "absolute_difference": anchor_difference}
            if not anchor_check["passed"]:
                quality["issues"].append("anchor reconstruction differs")
            quality["passed"] = not quality["issues"]
            loss_components = {name: design["weights"][name] * (result["moments"][name] - design["target"][name]) ** 2 for name in MOMENTS}
            record.update(status="ok" if quality["passed"] else "invalid", quality=quality, diagnostics=result["diagnostics"],
                          result=public_result(result, observer, case, design["market_index"]), anchor_check=anchor_check,
                          loss=float(sum(loss_components.values())), loss_components=loss_components,
                          equilibrium_sha256={key: array_hash(value) for key, value in result["equi"].items()},
                          error=None if quality["passed"] else "; ".join(quality["issues"]))
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
        record["seconds"] = time.perf_counter() - started
        atomic_json(path, record)
        counts["solved"] += 1
        counts[record["status"]] += 1
        print(f"{case['id']}: {record['status']} seconds={record['seconds']:.3f} error={record['error']}", flush=True)
    return dict(counts)


def collect(run_dir):
    run_dir = Path(run_dir).resolve()
    manifest, design = load_run(run_dir)
    _, estimation, _, _ = import_qmp(run_dir / "frozen_python")
    cases, issues, records_sha256, records_by_id = [], [], {}, {}
    for case in design["scenarios"]:
        path = run_dir / "records" / f"{case['id']}.json"
        try:
            record = read_json(path)
            validate_record(record, case, manifest, estimation)
            require(record["status"] == "ok", f"{record['status']}: {record['error']}")
            cases.append(record["result"])
            records_by_id[case["id"]]=record
            records_sha256[case["id"]] = file_hash(path)
        except Exception as exc:
            issues.append({"id": case["id"], "error": f"{type(exc).__name__}: {exc}"})
    matches=[]
    matched_points={point["case_id"]:point for path in ("overhead","seed") for point in design["paths"][path]["points"]}
    for point in matched_points.values():
        a,b=records_by_id.get(f"{point['case_id']}_reference"),records_by_id.get(f"{point['case_id']}_direct")
        equal=bool(a and b and a.get("equilibrium_sha256")==b.get("equilibrium_sha256"))
        matches.append({"case_id":point["case_id"],"reference_direct_arrays_equal":equal})
        if not equal: issues.append({"id":point["case_id"],"error":"matched direct/reference phi did not yield identical arrays"})
    audit = {"passed": not issues, "expected": len(design["scenarios"]), "ok": len(cases), "issues": issues,
             "matched_phi_checks":matches,
             "run_fingerprint": manifest["run_fingerprint"], "records_sha256": records_sha256}
    atomic_json(run_dir / "export_audit.json", audit)
    require(not issues, "incomplete or invalid scenarios; no complete teaching data bundle was published")
    bundle = {"schema_version": 1, "title": manifest["title"], "baseline_id": manifest["baseline_id"],
              "baseline_phi": manifest["baseline_phi"], "model_config": manifest["model_config"],
              "numerics": manifest["numerics"], "market_index": manifest["market_index"],
              "design": design, "scenarios": cases, "verification": read_json(run_dir / "baseline_verification.json"),
              "provenance": {"run_fingerprint": manifest["run_fingerprint"], "source_sha256": manifest["source_sha256"],
                             "runtime_versions": manifest["runtime_versions"], "export_audit_sha256": file_hash(run_dir / "export_audit.json")}}
    compact = json.dumps(safe_json(bundle), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    atomic_bytes(run_dir / "export/economy_data.json", (compact + "\n").encode("utf-8"))
    atomic_bytes(run_dir / "export/economy_data.js", ("window.ECONOMY_DATA=" + compact + ";\n").encode("utf-8"))
    return audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--source-python", required=True)
    prep.add_argument("--input-dir", required=True)
    prep.add_argument("--run-dir", required=True)
    run = commands.add_parser("solve")
    run.add_argument("--run-dir", required=True)
    run.add_argument("--shard-index", type=int, default=0)
    run.add_argument("--shard-count", type=int, default=1)
    run.add_argument("--limit", type=int)
    coll = commands.add_parser("collect")
    coll.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = prepare(args.source_python, args.input_dir, args.run_dir)
        print(json.dumps({k: result[k] for k in ("run_fingerprint", "scenario_count", "baseline_phi")}))
        return 0
    if args.command == "collect":
        result = collect(args.run_dir)
        print(json.dumps({k: result[k] for k in ("passed", "expected", "ok")}))
        return 0
    result = solve(args.run_dir, args.shard_index, args.shard_count, args.limit)
    print(json.dumps(result, sort_keys=True))
    return 1 if result["invalid"] or result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
