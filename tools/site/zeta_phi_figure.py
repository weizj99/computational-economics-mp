"""Draw lesson 02.3's figure of how ζ picks φ in the baseline economy.

In the first round of period 1 every potential firm operates, and the solver
gives each firm a break-even value Γ. For ζ < 1, φ is the first sorted value
whose cumulative share of firms is above ζ; for ζ ≥ 1, φ is ζ times the
largest value. The script repeats that first round for the page's baseline
economy (σ = 0.047041, N = 14.222682, ζ = 0.919212, seed 100, the page's
draws) and checks that the rule gives the φ of the full solve exactly, and the
φ that the page shows at the five points of the Fixed-cost control path. It
then draws φ against ζ for wide and narrow screens.

    python tools/site/zeta_phi_figure.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "model"), str(ROOT / "lessons/02_one_economy")]

from qmp import ModelConfig, Numerics, simulate  # noqa: E402
from qmp.draws import build_productivity  # noqa: E402
from qmp.equilibrium import _power, _prices, _sum_firms, solve_shares  # noqa: E402
from qmp.estimation import FIXED  # noqa: E402
import parameters_to_moments as page  # noqa: E402

UNIT = ROOT / "website/modules/02_one_economy"
FONTS = ROOT / "website/assets/fonts"
INK, MUTED, BLUE, COPPER, GRID, AXIS = "#20242b", "#59636e", "#2357a4", "#a85b2a", "#e3e7eb", "#aab4bd"
PATH = ("overhead_0", "overhead_1", "baseline", "overhead_3", "overhead_4")
SIZE = {False: (640, 400), True: (360, 340)}

for name in ("SourceSans3-Regular.ttf", "SourceSans3-Semibold.ttf"):
    font_manager.fontManager.addfont(FONTS / name)
plt.rcParams.update({"font.family": "Source Sans 3", "svg.fonttype": "path", "svg.hashsalt": "unit02-zeta",
                     "axes.unicode_minus": True, "savefig.pad_inches": .1})


def break_even_values(x, draws):
    """The sorted break-even values of the first round of period 1, as in _solve_period."""
    c, n = ModelConfig(), Numerics()
    productivity, u, _ = build_productivity(np.asarray(x, dtype=np.float64), c.markets, c.zbar, draws)
    z = productivity[:, :, 0]
    theta, eta = x[0], x[1]
    active = z > 0
    counts = active.sum(axis=0)
    s, mu, _ = solve_shares(z, theta, eta, c.gamma, n)
    wc, _, demand, sum_part = _prices(z, active, s, mu, counts, int(np.count_nonzero(counts)), theta, eta, c)
    demand_power = _power(demand, 1 / c.gamma, active)
    numerator = (mu - c.gamma) * c.varphibar * wc ** (c.varphi / c.alpha_cogs) * demand_power
    denominator = (c.alpha_cogs * c.psi_cogs * u * _power(z, 1 / c.gamma, active) / c.psi_sga * sum_part
                   + (mu - c.gamma) * demand_power * _sum_firms(u))
    values = numerator[active] / denominator[active]
    values.sort()
    return values


def phi_from(zeta, values):
    """The solver's rule: a rank for ζ < 1, a multiple of the largest value for ζ ≥ 1."""
    if zeta < 1:
        cdf = np.cumsum(np.full(values.size, 1 / values.size))
        return float(values[int(np.searchsorted(cdf, zeta, side="right"))])
    return float(values[-1] * zeta)


def style(ax, size):
    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=size, length=4)
    ax.grid(axis="y", color=GRID, linewidth=.8)
    ax.set_axisbelow(True)


def draw(values, points, mobile):
    width, height = SIZE[mobile]
    tick, label, note = (15, 16, 15) if mobile else (16, 17, 16)
    fig = plt.figure(figsize=(width / 72, height / 72), dpi=72, facecolor="white")
    ax = fig.add_axes([.17, .17, .78, .76] if mobile else [.105, .14, .86, .80])
    style(ax, tick)
    k = values.size
    # Below ζ = 1 the curve is the sorted values against the share of firms;
    # the top one per cent is kept in more detail, because it rises steeply.
    ranks = np.unique(np.concatenate([np.arange(0, k, 50), np.arange(int(.99 * k), k, 5), [k - 1]]))
    ax.plot((ranks + .5) / k, values[ranks] * 1e6, color=BLUE, linewidth=2, solid_capstyle="round", zorder=3)
    top = values[-1] * 1e6
    ax.plot([1, 1.1], [top, 1.1 * top], color=BLUE, linewidth=2, linestyle=(0, (4, 3)), zorder=3)
    ax.axvline(1, color=AXIS, linewidth=1, linestyle=(0, (2, 3)), zorder=1)
    base_zeta, base_phi = next((z, p) for case, z, p in points if case == "baseline")
    ax.plot([base_zeta, base_zeta, 0], [0, base_phi, base_phi], color=MUTED, linewidth=1,
            linestyle=(0, (2, 3)), zorder=2)
    for case, zeta, phi in points:
        baseline = case == "baseline"
        ax.scatter(zeta, phi, s=90 if baseline else 46, zorder=4, linewidths=1.6,
                   facecolors=COPPER if baseline else "white", edgecolors=COPPER if baseline else BLUE)
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 3.6)
    ax.set_xticks([0, .5, 1] if mobile else [0, .2, .4, .6, .8, 1])
    ax.set_yticks([0, 1, 2, 3])
    ax.set_xlabel("ζ", fontsize=label + 2, color=INK, labelpad=4)
    ax.set_ylabel("φ, millionths", fontsize=label, color=INK, labelpad=8)
    if mobile:
        ax.annotate(f"Baseline\nζ = {base_zeta:.3f}\nφ = {base_phi:.3f}", (base_zeta, base_phi), xytext=(.30, 2.55),
                    fontsize=note, color=INK, linespacing=1.3, va="center")
        ax.text(.035, 3.32, "From ζ = 1: ζ × largest", fontsize=note, color=INK, va="center")
    else:
        ax.annotate(f"Baseline: ζ = {base_zeta:.3f}, φ = {base_phi:.3f}", (base_zeta, base_phi),
                    xytext=(.36, 2.42), fontsize=note, color=INK, va="center",
                    arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 1, "shrinkB": 6})
        ax.text(.985, 3.36, f"From ζ = 1: φ = ζ × {top:.3f}, the largest value", fontsize=note, color=INK,
                ha="right", va="center")
        ax.text(.04, .62, "Sorted break-even values of all 140,000 firms", fontsize=note, color=INK, va="center")
    name = f"zeta_phi{'_mobile' if mobile else ''}.svg"
    fig.savefig(UNIT / "assets" / name, format="svg", dpi=72, facecolor="white", metadata={"Date": None})
    plt.close(fig)
    return name


def main():
    baseline = page.BASELINE
    x = [FIXED["theta"], FIXED["eta"], FIXED["rho"], baseline["sigma"], baseline["N"], baseline["zeta"]]
    firms = int(np.floor(baseline["N"]))
    draws = page.page_draws(firms, ModelConfig().markets, baseline["seed"])
    values = break_even_values(x, draws)
    solved = simulate(x, config=ModelConfig(), numerics=Numerics(), draws=draws)["phi"]
    if phi_from(baseline["zeta"], values) != solved:
        raise SystemExit(f"the rule gives {phi_from(baseline['zeta'], values)!r}, the solve {solved!r}")
    gallery = json.loads((UNIT / "economy_gallery.json").read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in gallery["cases"]}
    points = []
    for case_id in PATH:
        zeta = float(cases[case_id]["zeta_label"].split("=")[1])
        phi = phi_from(zeta, values) * 1e6
        if f"{phi:.3f} per million" != cases[case_id]["phi_label"]:
            raise SystemExit(f"{case_id}: φ = {phi:.3f}, the page shows {cases[case_id]['phi_label']}")
        points.append((case_id, zeta, phi))
    for mobile in (False, True):
        print("wrote", draw(values, points, mobile))
    print(f"{values.size} firms; φ = {solved * 1e6:.6f} millionths, the {np.searchsorted(values, solved) + 1}th "
          f"smallest value; largest value {values[-1] * 1e6:.6f}; value at ζ = 0.97 {phi_from(.97, values) * 1e6:.6f}")


if __name__ == "__main__":
    main()
