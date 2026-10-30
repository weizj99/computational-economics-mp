"""Unit 02: solve one of the page's economies again and check it against the page.

Lesson 02.3 traces saved economies from parameters to moments. Its baseline is
the centre of the year-2000 search box: sigma = 0.047041, N = 14.222682, so
M = 14 potential firms per market, and zeta = 0.919212, with 10,000 markets,
two periods and seed 100. The page draws productivity for 18 potential firms
per market and gives each economy the first M of them, so an economy with more
potential firms keeps the draws of the others. The script solves one of these
economies and prints what the page shows for it: phi, the operating firms, the
three moments, the employment totals, one firm of Market 1 and Market 1's
contributions. Each line is compared with the value saved for the page.

Run from the repository root (it needs NumPy and SciPy):
    python lessons/02_one_economy/parameters_to_moments.py
It takes about ten seconds. --case sigma_3 solves the next point on the sigma
path, and --firm 3 shows the third potential firm of Market 1.
"""
from __future__ import annotations

import os

# One linear-algebra thread, as when the page's economies were solved; with
# more threads the sales-weighted moments can change in the last digits.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "07_python"))

from qmp import ModelConfig, Numerics, generate_draws, simulate  # noqa: E402
from qmp.estimation import FIXED, MOMENT_NAMES  # noqa: E402

PAGE = ROOT / "06_teaching/modules/02_one_economy"
BASELINE = {"sigma": 0.047041, "N": 14.222682, "zeta": 0.919212, "seed": 100}
# Each of the page's four paths changes one input; the baseline lies on all of them.
PATHS = {"sigma": ("sigma", [0.032, 0.0395, 0.047041, 0.0545, 0.062]),
         "entrants": ("N", [10.0, 12.0, 14.222682, 16.0, 18.0]),
         "overhead": ("zeta", [0.70, 0.80, 0.919212, 0.97, 1.03]),
         "seed": ("seed", [100, 101, 102, 103, 104])}
BANK = 18  # potential firms per market in the page's draws
MOMENT_LABELS = ("Employment reallocation", "Sales-weighted markup", "SGA / total cost")
TOLERANCE = 1e-10


def cases():
    """Each point of the page's paths, with the name of its saved case.

    The page saved the baseline once, as "baseline"; its point on each path
    refers to it. The other 16 points are saved under their own names.
    """
    found = {"baseline": ("baseline", BASELINE)}
    for path, (name, levels) in PATHS.items():
        for index, value in enumerate(levels):
            case = {**BASELINE, name: value}
            found[f"{path}_{index}"] = ("baseline" if case == BASELINE else f"{path}_{index}", case)
    return found


def page_draws(firms, markets, seed):
    """The first `firms` rows of the page's 18-firm draws."""
    bank = generate_draws(BANK, markets, seed=seed)
    return {name: value[:firms] for name, value in bank.items()}


def read_page(case_id):
    """The page's saved readouts and moment-calculation tables for one case."""
    gallery = json.loads((PAGE / "task11_gallery.json").read_text(encoding="utf-8"))
    readouts = next(case for case in gallery["cases"] if case["id"] == case_id)
    script = (PAGE / "assets/moment_steps_data.js").read_text(encoding="utf-8")
    # The file sets one JavaScript variable to a JSON object.
    steps = json.loads(script[script.index("{"):script.rindex("}") + 1])["cases"][case_id]
    return readouts, steps


def calculate(result, config):
    """Employment, sales weights and Market 1's contributions, as the page builds them."""
    equi = result["equi"]
    n, fixed = equi["n_ijt"], equi["phi_ijt"]
    active = n > 0
    employment = np.where(active, n + fixed, 0.0)
    change = employment[:, :, 1] - employment[:, :, 0]
    E1, E2 = employment[:, :, 0].sum(), employment[:, :, 1].sum()
    average = 0.5 * (E1 + E2)

    # Sales weights and cost shares use period 1 and its operating firms.
    on, wage = active[:, :, 0], float(equi["W_t"][0])
    sales = np.where(on, equi["p_ijt"][:, :, 0] * equi["y_ijt"][:, :, 0], 0.0)
    sga = np.where(on, wage * fixed[:, :, 0] / config.psi_sga, 0.0)
    cost = np.where(on, config.gamma / config.alpha_cogs * wage * n[:, :, 0] / config.psi_cogs + sga, 0.0)
    share = np.divide(sga, cost, out=np.zeros_like(sga), where=on)
    weight = sales / sales[on].sum()
    markup = equi["mu_ijt"][:, :, 0]
    market1 = [np.abs(change[:, 0]).sum() / average,
               (weight[:, 0] * np.where(on[:, 0], markup[:, 0], 0.0)).sum(),
               (weight[:, 0] * share[:, 0]).sum()]
    return {"active": active, "n": np.where(active, n, 0.0), "fixed": np.where(active, fixed, 0.0),
            "employment": employment, "change": change, "E1": E1, "E2": E2,
            "JC": change[change > 0].sum(), "JD": -change[change < 0].sum(), "average": average,
            "on": on, "sales": sales, "total_sales": sales[on].sum(), "weight": weight, "markup": markup,
            "sga": sga, "cost": cost, "share": share, "market1": market1}


def lines(result, calc, firm, readouts, steps):
    """(heading or None, label, this run's values, the page's values) for every line."""
    m = [result["moments"][name] for name in MOMENT_NAMES]
    f, saved = firm - 1, steps["firms"][firm - 1]
    millionths = lambda value: f"{value * 1e6:.6f}"
    shown = [
        ("Readouts", "phi, fixed labor per operating firm", [f"{result['phi'] * 1e6:.3f} per million"],
         [readouts["phi_label"]]),
        (None, "Operating firms per market, period 1", [f"{result['equi']['Njt'][:, 0].mean():.3f}"],
         [readouts["mbar_label"]]),
        (None, MOMENT_LABELS[0], [f"{100 * m[0]:.3f}%"], [readouts["moments"]["reallocation_label"]]),
        (None, MOMENT_LABELS[1], [f"{m[1]:.4f}"], [readouts["moments"]["markup_label"]]),
        (None, MOMENT_LABELS[2], [f"{100 * m[2]:.3f}%"], [readouts["moments"]["sga_label"]]),
    ]
    totals = [("Period 1 employment E1", calc["E1"]), ("Period 2 employment E2", calc["E2"]),
              ("Job creation JC", calc["JC"]), ("Job destruction JD", calc["JD"]),
              ("Average employment (E1 + E2) / 2", calc["average"])]
    heading = "1 Employment changes: whole economy, model labor units"
    for (label, value), row in zip(totals, steps["employment_total_rows"]):
        shown.append((heading, label, [f"{value:.9f}"], [row[1]]))
        heading = None
    ratio = (calc["JC"] + calc["JD"]) / calc["average"]
    shown.append((None, "(JC + JD) / average employment", [f"{100 * ratio:.3f}%"],
                  [steps["employment_total_rows"][5][1]]))

    heading = f"1 Employment changes: Market 1, {saved['label']}, millionths (n + phi = e)"
    for t, row in enumerate(saved["employment_rows"]):
        values = [millionths(calc[key][f, 0, t]) for key in ("n", "fixed", "employment")]
        shown.append((heading, f"Period {t + 1}", values, row[1:]))
        heading = None
    active = bool(calc["on"][f, 0])
    sales = [millionths(calc["sales"][f, 0]) + " millionths", f"{calc['total_sales']:.6f}",
             f"{100 * calc['weight'][f, 0]:.6f}%", f"{calc['markup'][f, 0]:.6f}" if active else "—",
             millionths(calc["sga"][f, 0]) + " millionths", millionths(calc["cost"][f, 0]) + " millionths",
             f"{100 * calc['share'][f, 0]:.6f}%" if active else "—",
             f"{calc['weight'][f, 0] * (calc['markup'][f, 0] if active else 0.0):.9f}",
             f"{calc['weight'][f, 0] * calc['share'][f, 0]:.9f}"]
    labels = ("Sales = profit + total cost", "Whole-economy sales", "Economy sales weight w", "Markup mu",
              "SGA", "Total cost TC", "SGA / TC", "Markup contribution w * mu", "Cost-share contribution w * SGA/TC")
    heading = f"2 Sales weights: Market 1, {saved['label']}, period 1"
    for label, value, row in zip(labels, sales, saved["sales_rows"]):
        shown.append((heading, label, [value], [row[1]]))
        heading = None

    heading = "3 Add contributions: Market 1 + other 9,999 markets = all 10,000"
    for label, part, whole, row in zip(MOMENT_LABELS, calc["market1"], m, steps["contribution_rows"]):
        shown.append((heading, label, [f"{part:.9f}", f"{whole - part:.9f}", f"{whole:.9f}"], row[1:]))
        heading = None
    return shown


def full_precision(result, calc, firm, steps):
    """Differences from the full-precision values saved for the page.

    Returns the largest difference of the three moments, and the largest
    relative difference of the other saved values with their number. The page
    built JC, JD and sales from other saved totals, so these can differ in the
    last digit.
    """
    raw, f = steps["raw_derived"], firm - 1
    saved_firm = steps["firms"][f]["raw_derived"]
    moments = max(abs(result["moments"][name] - saved) for name, saved in zip(MOMENT_NAMES, raw["moments"]))
    pairs = [*zip(calc["market1"], raw["market_contribution"]),
             *((calc[key], raw[key]) for key in ("E1", "E2", "JC", "JD")),
             (calc["average"], raw["denominator"]), (calc["total_sales"], raw["total_sales"]),
             *zip(calc["employment"][f, 0], saved_firm["employment"]),
             (calc["change"][f, 0], saved_firm["change"]), (calc["sales"][f, 0], saved_firm["sales"]),
             (calc["weight"][f, 0], saved_firm["economy_sales_weight"]), (calc["sga"][f, 0], saved_firm["sga"]),
             (calc["cost"][f, 0], saved_firm["cost"]), (calc["share"][f, 0], saved_firm["cost_share"])]
    others = max(abs(mine - saved) / abs(saved) if saved else abs(mine) for mine, saved in pairs)
    return moments, others, len(pairs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    choices = cases()
    parser.add_argument("--case", default="baseline", choices=list(choices), metavar="CASE",
                        help="baseline, or a point on one of the page's paths, numbered 0 to 4 as on its "
                        "slider: sigma_0 to sigma_4, entrants_0 to entrants_4, overhead_0 to overhead_4 or "
                        "seed_0 to seed_4. The baseline is point 2 of the first three paths and point 0 of "
                        "the seed path")
    parser.add_argument("--firm", type=int, help="a potential firm of Market 1; by default the page's choice, "
                        "the first firm that operates in both periods")
    args = parser.parse_args(argv)
    (saved_case, case), config, numerics = choices[args.case], ModelConfig(), Numerics()
    firms = math.floor(case["N"])
    if args.firm is not None and not 1 <= args.firm <= firms:
        parser.error(f"choose a firm from 1 to {firms}")

    alias = " (the baseline)" if saved_case != args.case else ""
    print(f"Case {args.case}{alias}: sigma {case['sigma']:g}, N {case['N']:g} (M = {firms}), "
          f"zeta {case['zeta']:g}, seed {case['seed']}")
    started = time.perf_counter()
    x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], case["sigma"], case["N"], case["zeta"]]
    result = simulate(x, config=config, numerics=numerics,
                      draws=page_draws(firms, config.markets, case["seed"]))
    print(f"Solved {config.markets:,} markets, two periods, in {time.perf_counter() - started:.1f} s.")

    calc = calculate(result, config)
    both = np.flatnonzero(calc["active"][:, 0, 0] & calc["active"][:, 0, 1])
    firm = args.firm or (int(both[0]) + 1 if both.size else 1)
    readouts, steps = read_page(saved_case)
    shown = lines(result, calc, firm, readouts, steps)
    for heading, label, mine, saved in shown:
        if heading:
            print(f"\n{heading}")
        same = list(mine) == list(saved)
        text = " + ".join(mine[:-1]) + " = " + mine[-1] if len(mine) == 3 else mine[0]
        page = " + ".join(saved[:-1]) + " = " + saved[-1] if len(saved) == 3 else saved[0]
        print(f"  {label:<36}{text:>34}  {'same' if same else 'page: ' + page}")

    matching = sum(list(mine) == list(saved) for _, _, mine, saved in shown)
    moments, others, count = full_precision(result, calc, firm, steps)
    print(f"\n{matching} of {len(shown)} lines match the page.")
    print(f"At full precision the three moments differ from the saved values by at most {moments:.3g}, "
          f"and {count} other saved values by at most {others:.3g} relative.")
    if not result["diagnostics"]["entry_stopping_rule_met"]:
        print("The entry iteration limit was reached; the solve is not complete.")
        return 2
    return 0 if matching == len(shown) and max(moments, others) <= TOLERANCE else 1


if __name__ == "__main__":
    raise SystemExit(main())
