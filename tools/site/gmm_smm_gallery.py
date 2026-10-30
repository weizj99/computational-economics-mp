"""Generate unit 01's reproducible moment-matching gallery.

This is an independent Python teaching implementation, not an original-author
replication package. Generation and validation are performed once; the browser
only selects saved figures and values. Requires NumPy, SciPy and Matplotlib.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar


FIRMS = 5
SECTORS = 100
ETA = 5.75
TRUE_SIGMA = 1.0
DATA_SEED = 1
SIMULATION_SEEDS = (2, 3)
SIMULATION_COUNTS = (1, 10, 100, 1000)
SIGMA_GRID = np.linspace(0.75, 1.25, 51)
BLUE = "#185879"
COPPER = "#a45d3c"
INK = "#1d2b38"
MUTED = "#66747b"
PAPER = "#fdfdfb"


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_hash(array):
    array = np.ascontiguousarray(array)
    return hashlib.sha256(array.tobytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8")


def statistic(normal_draws, sigma):
    """Mean unbiased within-sector variance of log sales under the task model.

    Log sales differ from (eta-1)*log productivity by a sector constant.
    The constant vanishes from within-sector variance. The last array axis
    indexes the five firms; the penultimate axis indexes the 100 sectors.
    """
    log_sales_up_to_sector_constant = (ETA - 1) * sigma * np.asarray(normal_draws)
    return np.var(log_sales_up_to_sector_constant, axis=-1, ddof=1).mean(axis=-1)


def theoretical_moment(sigma):
    return (ETA - 1) ** 2 * np.asarray(sigma) ** 2


def svg_text(x, y, text, *, size=15, fill=INK, anchor="start", weight="400", extra=""):
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {extra}>{html.escape(str(text))}</text>')


def nice_ticks(maximum):
    magnitude = 10 ** math.floor(math.log10(maximum / 4))
    fraction = maximum / 4 / magnitude
    step = next((s for s in (1, 2, 2.5, 5, 10) if s >= fraction), 10) * magnitude
    top = math.ceil(maximum / step) * step
    return np.arange(0, top + step * .1, step), top


# Type sizes in SVG units. The page shows desktop SVGs at about 0.7-0.8 of their
# width and mobile SVGs at about half, so tick labels appear at about 14 px.
SIZES = {False: {"title": 27, "subtitle": 19, "tick": 19, "label": 20, "note": 18},
         True: {"title": 38, "subtitle": 27, "tick": 28, "label": 29, "note": 26}}


def panel_svg(x0, y0, width, height, curves, current_index, target,
              y_limit, title, subtitle, y_label, show_minima=False, mobile=False):
    # A title or subtitle may hold line breaks for a narrow figure.
    size = SIZES[mobile]
    out, baseline = [], y0 + 1.1 * size["title"]
    for line in title.split("\n"):
        out.append(svg_text(x0 + 9, baseline, line, size=size["title"]))
        baseline += 1.25 * size["title"]
    baseline += 1.05 * size["subtitle"] + 8 - 1.25 * size["title"]
    for line in subtitle.split("\n"):
        out.append(svg_text(x0 + 9, baseline, line, size=size["subtitle"], fill=MUTED))
        baseline += 1.35 * size["subtitle"]
    left = x0 + (108 if mobile else 78)
    top = baseline - 1.35 * size["subtitle"] + .36 * size["tick"] + (22 if mobile else 16)
    right = x0 + width - (30 if mobile else 22)
    bottom = y0 + height - (102 if mobile else 80)
    plot_w, plot_h = right - left, bottom - top
    sx = lambda x: left + (x - SIGMA_GRID[0]) / (SIGMA_GRID[-1] - SIGMA_GRID[0]) * plot_w
    sy = lambda y: bottom - y / y_limit * plot_h
    ticks = np.linspace(0, y_limit, 5)
    for tick in ticks:
        y = sy(tick)
        out.append(f'<path d="M{left:.2f},{y:.2f}H{right:.2f}" stroke="#e4e9e8" stroke-width="1"/>')
        out.append(svg_text(left - (16 if mobile else 12), y + .36 * size["tick"],
                            f"{tick:.0f}" if y_limit >= 20 else f"{tick:.2f}",
                            size=size["tick"], fill=MUTED, anchor="end"))
    out.append(f'<path d="M{left:.2f},{top:.2f}V{bottom:.2f}H{right:.2f}" fill="none" stroke="#a3afb3"/>')
    tick_baseline = bottom + (22 if mobile else 16) + .75 * size["tick"]
    for tick in (.75, .85, .95, 1.05, 1.15, 1.25):
        x = sx(tick)
        out.append(f'<path d="M{x:.2f},{bottom:.2f}v5" stroke="#a3afb3"/>')
        out.append(svg_text(x, tick_baseline, f"{tick:.2f}", size=size["tick"], fill=MUTED, anchor="middle"))
    out.append(svg_text((left + right) / 2, tick_baseline + .3 * size["tick"] + (14 if mobile else 12) + .75 * size["label"],
                        "Candidate σA", size=size["label"], fill=MUTED, anchor="middle"))
    axis_x = x0 + (30 if mobile else 21)
    out.append(svg_text(axis_x, (top + bottom) / 2, y_label,
                        size=size["tick"], fill=MUTED, anchor="middle",
                        extra=f'transform="rotate(-90 {axis_x:.2f} {(top+bottom)/2:.2f})"'))
    if target is not None:
        out.append(f'<path d="M{left:.2f},{sy(target):.2f}H{right:.2f}" stroke="#7f8b91" stroke-width="1.4" stroke-dasharray="5 5"/>')
        out.append(svg_text(right - 4, sy(target) - (12 if mobile else 8), "observed",
                            size=size["note"], fill=MUTED, anchor="end"))
    marker_x = sx(SIGMA_GRID[current_index])
    out.append(f'<path d="M{marker_x:.2f},{top:.2f}V{bottom:.2f}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="3 5"/>')
    for curve_index, (curve, color) in enumerate(zip(curves, (BLUE, COPPER))):
        path = " ".join(("M" if i == 0 else "L") + f"{sx(x):.3f},{sy(y):.3f}" for i, (x, y) in enumerate(zip(SIGMA_GRID, curve)))
        dash = 'stroke-dasharray="8 5"' if curve_index else ""
        out.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3" {dash}/>')
        out.append(f'<circle cx="{marker_x:.3f}" cy="{sy(curve[current_index]):.3f}" r="4.8" fill="{PAPER}" stroke="{color}" stroke-width="2.4"/>')
        if show_minima:
            index = int(np.argmin(curve))
            px, py = sx(SIGMA_GRID[index]), sy(curve[index])
            out.append(f'<path d="M{px:.3f},{py-6:.3f}l6,6l-6,6l-6,-6Z" fill="{color}" stroke="{PAPER}" stroke-width="1"/>')
    return "\n".join(out)


def render_svg(group, current_index, observed, moment_y, loss_y, mobile=False):
    width, height = (680, 1080) if mobile else (1360, 570)
    if mobile:
        positions = [(0, 0, 680, 525), (0, 530, 680, 525)]
    else:
        positions = [(0, 0, 665, 550), (695, 0, 665, 550)]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Direct and simulated moment matching</title>',
             f'<desc id="desc">Candidate sigma {SIGMA_GRID[current_index]:.2f}, {group["S"]} simulated data sets, simulation seed {group["seed"]}. Left or upper panel: moments. Right or lower panel: squared error. Same axes in every view.</desc>',
             f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
             '<g font-family="Arial,Helvetica,sans-serif">']
    parts.append(panel_svg(*positions[0], (group["direct"], group["simulated"]), current_index,
                           observed, moment_y, "01  Match the moment", "One fixed observed sample", "Variance of log sales",
                           mobile=mobile))
    parts.append(panel_svg(*positions[1], (group["direct_loss"], group["simulated_loss"]), current_index,
                           None, loss_y, "02  Minimize the discrepancy", "Both criteria use the same vertical scale", "Squared moment error",
                           show_minima=True, mobile=mobile))
    parts += ["</g>", "</svg>"]
    return "\n".join(parts) + "\n"


def representative_png(groups, observed, moment_y, loss_y, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#a3afb3", "svg.fonttype": "none"})
    for seed, count, index in ((2, 1, 25), (2, 1000, 25), (3, 10, 35)):
        group = groups[f"{seed}_{count}"]
        fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.7))
        for ax, curves, upper, title, ylabel in zip(axes,
                ((group["direct"], group["simulated"]), (group["direct_loss"], group["simulated_loss"])),
                (moment_y, loss_y), ("01  Match the moment", "02  Minimize the discrepancy"),
                ("Variance of log sales", "Squared moment error")):
            for curve, color, style, label in zip(curves, (BLUE, COPPER), ("-", "--"), ("Direct / GMM", "Simulated / SMM")):
                ax.plot(SIGMA_GRID, curve, color=color, ls=style, lw=2.2, label=label)
                ax.scatter([SIGMA_GRID[index]], [curve[index]], edgecolor=color, facecolor=PAPER, s=35, zorder=4)
                if ylabel == "Squared moment error":
                    minimum = int(np.argmin(curve))
                    ax.scatter([SIGMA_GRID[minimum]], [curve[minimum]], marker="D", color=color, s=30, zorder=5)
            ax.axvline(SIGMA_GRID[index], color=INK, lw=1, ls=":")
            ax.set(xlim=(.75, 1.25), ylim=(0, upper), xlabel="Candidate σA", ylabel=ylabel)
            ax.set_title(title, loc="left", pad=14, fontsize=14)
            ax.grid(axis="y", color="#e4e9e8", lw=.7)
            ax.set_axisbelow(True)
        axes[0].axhline(observed, color="#7f8b91", lw=1.2, ls="--", label="Observed moment")
        axes[0].legend(frameon=False, fontsize=9, loc="upper left")
        fig.text(.07, .025, f"Unit 01 · fixed observed sample · S = {count} · simulation seed {seed} · current σA = {SIGMA_GRID[index]:.2f}\nDiamonds: best displayed-grid candidates. The two objective curves share one scale.", fontsize=9, color=MUTED)
        fig.subplots_adjust(left=.07, right=.98, top=.89, bottom=.20, wspace=.28)
        fig.savefig(output / f"preview_s{seed}_n{count}_k{index:02d}.png", dpi=300, facecolor=PAPER)
        plt.close(fig)


def repeated_estimation(output):
    """1000 independent observed samples and simulation sequences."""
    rows = []
    for seed in range(101, 1101):
        data = np.random.Generator(np.random.PCG64(seed)).standard_normal((SECTORS, FIRMS))
        observed = float(statistic(data, TRUE_SIGMA))
        # The stream tag prevents overlaps with observed-data integer seeds.
        omega = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, 20000]))).standard_normal((10, SECTORS, FIRMS))
        coefficients = np.var(omega, axis=-1, ddof=1).mean(axis=-1)
        rows.append({"data_seed": seed, "simulation_seed_sequence": [seed, 20000],
                     "observed_moment": observed, "gmm": math.sqrt(observed)/(ETA-1),
                     "smm_S1": math.sqrt(observed / float(coefficients[0]))/(ETA-1),
                     "smm_S10": math.sqrt(observed / float(coefficients.mean()))/(ETA-1)})
    baseline = TRUE_SIGMA / math.sqrt(2 * SECTORS * (FIRMS - 1))
    summary = []
    for key, count in (("gmm", None), ("smm_S1", 1), ("smm_S10", 10)):
        estimates = np.array([r[key] for r in rows])
        theoretical_sd = baseline if count is None else baseline * math.sqrt(1 + 1/count)
        summary.append({"method": "GMM" if count is None else f"SMM · S = {count}",
                        "mean_estimate": float(estimates.mean()), "empirical_sd": float(estimates.std(ddof=1)),
                        "asymptotic_sd": theoretical_sd, "repetitions": len(rows),
                        "ratio_empirical_to_asymptotic_sd": float(estimates.std(ddof=1))/theoretical_sd})
    write_json(output / "repeated_estimates.json", {"repetitions": len(rows), "data_seeds": [101, 1100],
        "simulation_stream": "SeedSequence([data_seed, 20000]); separate from observed data; S1 is the first of the S10 sequence",
        "estimates": rows, "summary": summary})
    return rows, summary


def refreshed_objective(observed, fixed_group, output):
    """Redraw simulation input at each candidate, holding data fixed."""
    refreshed = []
    # Initialize once outside the objective loop. Each subsequent evaluation
    # advances this stream; it does not reset a seed inside the objective.
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([2, 30000])))
    for sigma in SIGMA_GRID:
        omega = rng.standard_normal((SECTORS, FIRMS))
        simulated = float(statistic(omega, sigma))
        refreshed.append((simulated-observed)**2)
    refreshed = np.array(refreshed)
    _, limit = nice_ticks(max(float(refreshed.max()), float(fixed_group['simulated_loss'].max())) * 1.1)
    curves = (fixed_group["simulated_loss"], refreshed)
    title, subtitle = "Common random numbers make comparisons clearer", "S = 1; the observed data are identical in both cases"
    # Wide screens: the key sits in one row under the panel. Narrow screens: the
    # title, subtitle and key each take two lines.
    for name, (width, height), panel_height, breaks, keys in (
            ("random_numbers.svg", (920, 470), 440, (), ((180, 452), (520, 452))),
            ("random_numbers_mobile.svg", (680, 720), 606, ("make", "are"), ((9, 640), (9, 690)))):
        mobile = name.endswith("_mobile.svg")
        lines = [title, subtitle]
        for word in breaks:
            lines = [line.replace(f" {word} ", f" {word}\n", 1) for line in lines]
        panel = panel_svg(0, 0, width, panel_height, curves, 25, None, limit, *lines, "Squared moment error", mobile=mobile)
        size = SIZES[mobile]["subtitle"]
        key = ""
        for (x, y), color, dash, label in zip(keys, (BLUE, COPPER), ("", ' stroke-dasharray="8 5"'),
                                             ("Same draws at every candidate", "Fresh draws at every candidate")):
            key += (f'<path d="M{x},{y}h{size * 2}" stroke="{color}" stroke-width="3"{dash}/>'
                    + svg_text(x + size * 2.5, y + .36 * size, label, size=size))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="rn-title">'
               '<title id="rn-title">SMM objective with fixed versus refreshed simulation draws</title>'
               f'<rect width="{width}" height="{height}" fill="{PAPER}"/><g font-family="Arial,Helvetica,sans-serif">{panel}'
               f'{key}</g></svg>\n')
        (output / name).write_text(svg, encoding="utf-8")
    write_json(output / "random_numbers.json", {"sigma_grid": SIGMA_GRID.tolist(),
        "fixed_draw_seed": 2, "redraw_seed_sequence": "[2,30000]",
        "redraw_rng_policy": "advance_stream: initialize once before the loop; every objective evaluation consumes the next draws without resetting the seed",
        "fixed_objective": fixed_group["simulated_loss"].tolist(), "refreshed_objective": refreshed.tolist(),
        "observed_moment": observed, "simulation_count": 1})


def validate(observed_draws, simulation_draws, observed, groups, repetition_summary):
    checks = []
    def check(name, passed, **details):
        checks.append({"name": name, "passed": bool(passed), **details})
    repeated_data = np.random.Generator(np.random.PCG64(DATA_SEED)).standard_normal((SECTORS, FIRMS))
    check("same observed seed reproduces every draw", np.array_equal(repeated_data, observed_draws))
    check("observed and simulation streams differ", DATA_SEED not in SIMULATION_SEEDS)
    check("repetition exercise contains the required 1000 data samples", all(r['repetitions'] == 1000 for r in repetition_summary))
    advancing_rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([2, 30000])))
    first_draw = advancing_rng.standard_normal((SECTORS, FIRMS))
    second_draw = advancing_rng.standard_normal((SECTORS, FIRMS))
    first_same_sigma = float(statistic(first_draw, TRUE_SIGMA))
    second_same_sigma = float(statistic(second_draw, TRUE_SIGMA))
    check("refreshed objective advances stream on consecutive calls at the same sigma",
          not np.array_equal(first_draw, second_draw) and first_same_sigma != second_same_sigma,
          sigma=TRUE_SIGMA, first_moment=first_same_sigma, second_moment=second_same_sigma,
          policy="advance_stream; seed initialized once outside the evaluation loop")
    max_formula_error, optimizer_errors = 0.0, []
    gmm_exact = math.sqrt(observed) / (ETA - 1)
    gmm_numeric = minimize_scalar(lambda s: float((theoretical_moment(s) - observed) ** 2),
                                  bracket=(.8, 1.2), method="brent", options={"xtol": 1e-13})
    optimizer_errors.append(abs(float(gmm_numeric.x) - gmm_exact))
    check("GMM numerical minimum matches analytic minimum", gmm_numeric.success and optimizer_errors[-1] <= 1e-8,
          absolute_error=optimizer_errors[-1])
    for seed in SIMULATION_SEEDS:
        repeated = np.random.Generator(np.random.PCG64(seed)).standard_normal((max(SIMULATION_COUNTS), SECTORS, FIRMS))
        check(f"simulation stream {seed} exactly reproducible", np.array_equal(repeated, simulation_draws[seed]))
        for count in SIMULATION_COUNTS:
            group = groups[f"{seed}_{count}"]
            direct_loop = np.array([float(np.mean(statistic(simulation_draws[seed][:count], s))) for s in SIGMA_GRID])
            discrepancy = float(np.max(np.abs(direct_loop - group["simulated"])))
            max_formula_error = max(max_formula_error, discrepancy)
            numeric = minimize_scalar(lambda s: float((np.mean(statistic(simulation_draws[seed][:count], s)) - observed) ** 2),
                                      bracket=(.8, 1.2), method="brent", options={"xtol": 1e-13})
            error = abs(float(numeric.x) - group["smm_exact"])
            optimizer_errors.append(error)
            check(f"SMM stream {seed}, S={count}: analytic and numerical minimum", numeric.success and error <= 1e-8,
                  absolute_error=error)
            check(f"SMM stream {seed}, S={count}: mean statistic equals scaling formula", discrepancy <= 1e-11,
                  maximum_absolute_error=discrepancy)
    # For normal firms, J(I-1)*v_hat/v is exactly chi-square with J(I-1) d.f.
    # This fast check samples that exact distribution, not a different model.
    df = SECTORS * (FIRMS - 1)
    repetitions = 20000
    rng = np.random.Generator(np.random.PCG64(71010))
    data_coefficients = rng.chisquare(df, size=repetitions) / df
    gmm_replications = np.sqrt(data_coefficients)
    se_rows = []
    for count in SIMULATION_COUNTS:
        sim_coefficients = rng.chisquare(count * df, size=repetitions) / (count * df)
        moment_sd_empirical = float((theoretical_moment(TRUE_SIGMA) * sim_coefficients).std(ddof=1))
        moment_sd_exact = float(theoretical_moment(TRUE_SIGMA) * math.sqrt(2 / (count * df)))
        smm_sd_empirical = float(np.sqrt(data_coefficients / sim_coefficients).std(ddof=1))
        smm_sd_delta = math.sqrt((1 + 1 / count) / (2 * df))
        ratio = moment_sd_empirical / moment_sd_exact
        check(f"simulation moment standard error S={count}", .96 < ratio < 1.04,
              exact_standard_error=moment_sd_exact, monte_carlo_standard_deviation=moment_sd_empirical,
              ratio=ratio, repetitions=repetitions)
        se_rows.append({"S": count, "moment_sd_exact": moment_sd_exact,
                        "moment_sd_monte_carlo": moment_sd_empirical, "smm_sigma_sd_monte_carlo": smm_sd_empirical,
                        "smm_sigma_sd_delta_approximation": smm_sd_delta})
    return {"passed": all(c["passed"] for c in checks), "checks": checks,
            "formula_maximum_absolute_error": max_formula_error,
            "optimizer_maximum_absolute_error": max(optimizer_errors),
            "simulation_error_check": {"method": "exact chi-square distribution of the normal unbiased within-sector variance",
                "repetitions": repetitions, "seed": 71010, "degrees_of_freedom": df,
                "gmm_sigma_sd_monte_carlo": float(gmm_replications.std(ddof=1)),
                "gmm_sigma_sd_delta_approximation": math.sqrt(1 / (2 * df)), "rows": se_rows},
            "task4_repetition_summary": repetition_summary,
            "limitations": ["This is a new teaching reference; no earlier result table was available to compare with.",
                            "Five-firm sample variance uses ddof=1, then averages over sectors.",
                            "The large-sample estimator standard deviations are approximations, not exact finite-sample equalities.",
                            "PCG64 seeds reproduce this Python version."]}


def generate(output):
    output = Path(output)
    frames_dir = output / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    observed_draws = np.random.Generator(np.random.PCG64(DATA_SEED)).standard_normal((SECTORS, FIRMS))
    observed = float(statistic(observed_draws, TRUE_SIGMA))
    simulations = {seed: np.random.Generator(np.random.PCG64(seed)).standard_normal(
        (max(SIMULATION_COUNTS), SECTORS, FIRMS)) for seed in SIMULATION_SEEDS}
    direct = theoretical_moment(SIGMA_GRID)
    groups = {}
    for seed in SIMULATION_SEEDS:
        coefficients = np.var(simulations[seed], axis=-1, ddof=1).mean(axis=-1)
        for count in SIMULATION_COUNTS:
            coefficient = float(coefficients[:count].mean())
            simulated = direct * coefficient
            groups[f"{seed}_{count}"] = {"seed": seed, "S": count, "coefficient": coefficient,
                "direct": direct, "simulated": simulated,
                "direct_loss": (direct - observed) ** 2, "simulated_loss": (simulated - observed) ** 2,
                "smm_exact": math.sqrt(observed / coefficient) / (ETA - 1)}
    repetition_rows, repetition_summary = repeated_estimation(output)
    validation = validate(observed_draws, simulations, observed, groups, repetition_summary)
    write_json(output / "validation_report.json", validation)
    if not validation["passed"]:
        raise RuntimeError("Unit 01 validation failed; no completed gallery is published")
    _, moment_y = nice_ticks(max(float(g["simulated"].max()) for g in groups.values()) * 1.10)
    _, loss_y = nice_ticks(max(max(float(g["direct_loss"].max()), float(g["simulated_loss"].max())) for g in groups.values()) * 1.10)
    gallery = {"schema_version": 1, "observed_label": f"{observed:.4f}",
               "gmm_label": f"{math.sqrt(observed)/(ETA-1):.4f}",
               "display_note": "One fixed observed sample · common random numbers within each stream · 51 displayed candidates · no smoothing",
               "repetition_rows": [{"method": r["method"], "mean_label": f"{r['mean_estimate']:.4f}",
                   "sd_label": f"{r['empirical_sd']:.4f}", "approximation_label": f"{r['asymptotic_sd']:.4f}"} for r in repetition_summary],
               "estimate_rows": [{"S_label": str(count), "stream_A_label": f"{groups[f'2_{count}']['smm_exact']:.4f}",
                   "stream_B_label": f"{groups[f'3_{count}']['smm_exact']:.4f}"} for count in SIMULATION_COUNTS],
               "groups": {}}
    manifest = {"schema_version": 1, "exercise": "Unit 01: direct and simulated within-sector log-sales variance",
        "authorship": "Independent Python teaching implementation", "firms_per_sector": FIRMS,
        "sectors": SECTORS, "eta": ETA, "true_sigma_A": TRUE_SIGMA,
        "task_other_parameters": {"theta": 1.2, "P": 1, "phibar": 1, "varphi": .25, "mu_A": 0},
        "exact_reduction": "log revenue = (eta-1)*sigma_A*epsilon + sector common term; common term cancels from within-sector sample variance. This module does not call the full QMP solver.",
        "variance_ddof": 1, "data_seed": DATA_SEED, "simulation_seeds": list(SIMULATION_SEEDS),
        "simulation_counts": list(SIMULATION_COUNTS), "sigma_grid": SIGMA_GRID.tolist(),
        "rng": "NumPy PCG64, data and simulation use separately initialized, distinct seeds",
        "draw_order": "observed (sectors,firms); simulation (replications,sectors,firms); normal draws scaled by candidate sigma",
        "same_draws_across_candidates": True, "nested_replications_across_S": True,
        "task5_redraw_rng_policy": "advance_stream: initialize SeedSequence([2,30000]) once; consume new draws for each candidate without reseeding",
        "observed_moment": observed, "gmm_exact": math.sqrt(observed)/(ETA-1),
        "observed_draws_sha256": array_hash(observed_draws),
        "simulation_draws_sha256": {str(seed): array_hash(draws) for seed, draws in simulations.items()},
        "source_sha256": file_hash(Path(__file__)), "common_axes": {"moment": [0, moment_y], "loss": [0, loss_y]},
        "groups": {}, "files": {}, "validation_passed": True}
    for key, group in groups.items():
        entry = {"smm_label": f"{group['smm_exact']:.4f}", "caption":
                 "Every curve uses the same observed target. Both objective curves share one vertical scale, fixed across all views. Diamonds mark the best points on the displayed 51-point grid; the continuous estimates appear below.", "frames": []}
        gmm_grid_index = int(np.argmin(group["direct_loss"]))
        smm_grid_index = int(np.argmin(group["simulated_loss"]))
        manifest["groups"][key] = {"coefficient": group["coefficient"], "smm_exact": group["smm_exact"],
            "gmm_grid_minimum": float(SIGMA_GRID[gmm_grid_index]), "smm_grid_minimum": float(SIGMA_GRID[smm_grid_index]),
            "smm_moment_standard_error_at_true_sigma": float(theoretical_moment(TRUE_SIGMA) * math.sqrt(2/(SECTORS*(FIRMS-1)*group['S'])))}
        for index, sigma in enumerate(SIGMA_GRID):
            stem = f"s{group['seed']}_n{group['S']}_k{index:02d}"
            for mobile in (False, True):
                suffix = "_mobile" if mobile else ""
                path = frames_dir / f"{stem}{suffix}.svg"
                path.write_text(render_svg(group, index, observed, moment_y, loss_y, mobile), encoding="utf-8")
                manifest["files"][str(path.relative_to(output)).replace("\\", "/")] = file_hash(path)
            entry["frames"].append({"sigma_label": f"{sigma:.2f}",
                "image": f"assets/frames/{stem}.svg", "mobile_image": f"assets/frames/{stem}_mobile.svg",
                "direct_label": f"{group['direct'][index]:.4f}", "simulated_label": f"{group['simulated'][index]:.4f}",
                "direct_loss_label": f"squared error {group['direct_loss'][index]:.4f}",
                "simulated_loss_label": f"squared error {group['simulated_loss'][index]:.4f}",
                "alt": f"At sigma {sigma:.2f}, the direct moment is {group['direct'][index]:.4f}, the simulated moment is {group['simulated'][index]:.4f}, and the observed target is {observed:.4f}. S equals {group['S']}; simulation seed {group['seed']}."})
        gallery["groups"][key] = entry
    write_json(output / "gallery_data.json", gallery)
    (output / "gallery_data.js").write_text("window.GMM_SMM_GALLERY = " + json.dumps(gallery, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    np.savez_compressed(output / "random_inputs.npz", observed=observed_draws,
                        simulation_2=simulations[2], simulation_3=simulations[3])
    refreshed_objective(observed, groups["2_1"], output)
    representative_png(groups, observed, moment_y, loss_y, output)
    for path in output.iterdir():
        if path.is_file() and path.name != "manifest.json":
            manifest["files"][path.name] = file_hash(path)
    manifest["frame_count"] = 408
    manifest["gallery_svg_count"] = 816
    manifest["additional_svg_count"] = 2
    manifest["representative_pngs"] = ["preview_s2_n1_k25.png", "preview_s2_n1000_k25.png", "preview_s3_n10_k35.png"]
    write_json(output / "manifest.json", manifest)
    print(json.dumps({"validation_passed": True, "frame_count": 408, "gallery_svg_count": 816,
                      "observed_moment": observed, "gmm_estimate": manifest["gmm_exact"],
                      "output": str(output)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[2] / "website/modules/01_gmm_smm/assets")
    args = parser.parse_args()
    generate(args.output_dir)


if __name__ == "__main__":
    main()
