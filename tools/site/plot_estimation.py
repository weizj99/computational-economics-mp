"""Draw unit 03's search and annual figures from its saved results.

The figures use the course's type (Source Sans 3) and colours, and leave titles
to the page. The script reads only saved results in the unit's assets folder:
the candidate table (search_results.csv), the annual winners
(annual_parameters.csv) and the winners solved again with three new draws
(fresh_draws.csv, from fresh_draws.py). It writes, for every year, the scatter
of the 512 candidates in sigma and N, and three annual figures (fit to the
data, the selected parameters and the fit with new draws), each for wide and
narrow screens. It then moves the clickable point of every candidate in the
page's data (gallery_data.js) to its place on the new scatter, and stores the
error of the fit with new draws there.

    python tools/site/plot_estimation.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, LogNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "website/modules/03_estimation/assets"
FONTS = ROOT / "website/assets/fonts"
INK, MUTED, BLUE, COPPER, GRID, AXIS = "#20242b", "#59636e", "#2357a4", "#a85b2a", "#e3e7eb", "#aab4bd"
# Loss on a log scale: dark blue for the best candidates, pale for the worst.
LOSS = LinearSegmentedColormap.from_list("loss", ["#14376b", "#2357a4", "#8fb0d8", "#dfe7f1"])
MOMENTS = ("employment_reallocation_rate", "markup_sales_weighted", "sga_cost_share_sales_weighted")
SCALES = (100, 1, 100)
# Scatter sizes in pixels, wide and narrow.
SCATTER = {False: (720, 450), True: (420, 420)}

for name in ("SourceSans3-Regular.ttf", "SourceSans3-Semibold.ttf"):
    font_manager.fontManager.addfont(FONTS / name)
plt.rcParams.update({"font.family": "Source Sans 3", "svg.fonttype": "path", "svg.hashsalt": "unit03",
                     "axes.formatter.useoffset": False, "axes.unicode_minus": True,
                     "savefig.pad_inches": .1})


def read_rows(name):
    with (ASSETS / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def style(ax, size):
    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=size, length=4)
    ax.grid(axis="y", color=GRID, linewidth=.8)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(ASSETS / name, format="svg", dpi=72, facecolor="white", metadata={"Date": None})
    plt.close(fig)


def scatter(year, rows, box, mobile):
    """The 512 candidates of one year, and each one's place in image pixels."""
    # The page shows the wide figure at about 600-700 px, so it is drawn near that size.
    width, height = SCATTER[mobile]
    tick, label = (17, 18) if mobile else (17, 19)
    fig = plt.figure(figsize=(width / 72, height / 72), dpi=72, facecolor="white")
    ax = fig.add_axes([.19, .17, .60, .70] if mobile else [.115, .15, .70, .74])
    style(ax, tick)
    loss = np.array([float(r["loss"]) for r in rows])
    ax.scatter([float(r["sigma"]) for r in rows], [float(r["N"]) for r in rows], c=loss, cmap=LOSS,
               norm=LogNorm(vmin=max(loss.min(), 1e-12), vmax=loss.max()),
               s=14 if mobile else 26, alpha=.9, linewidths=0, zorder=3)
    best = min(rows, key=lambda r: int(r["rank"]))
    ax.scatter(float(best["sigma"]), float(best["N"]), marker="D", s=70 if mobile else 130,
               facecolors="none", edgecolors=INK, linewidths=1.5, zorder=4)
    ax.set_xlim(box["sigma_lo"], box["sigma_hi"])
    ax.set_ylim(box["N_lo"], box["N_hi"])
    ax.xaxis.set_major_locator(MaxNLocator(3 if mobile else 6))
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.set_xlabel("Dispersion σ", fontsize=label, color=INK, labelpad=8)
    ax.set_ylabel("Potential firms N", fontsize=label, color=INK, labelpad=8)
    cax = fig.add_axes([.84, .21, .03, .56] if mobile else [.86, .20, .022, .60])
    bar = fig.colorbar(ax.collections[0], cax=cax)
    bar.ax.tick_params(labelsize=tick - 1, colors=MUTED, length=3)
    bar.outline.set_visible(False)
    cax.set_title("Loss", fontsize=tick, color=INK, pad=10, loc="left")
    fig.legend(handles=[Line2D([], [], marker="D", linestyle="none", markersize=9, markerfacecolor="none",
                               markeredgecolor=INK, markeredgewidth=1.5)],
               labels=["Best of the 512"], loc="upper left", frameon=False, fontsize=tick,
               bbox_to_anchor=(.17 if mobile else .105, .995), handletextpad=.4, borderaxespad=.2)
    fig.canvas.draw()
    pixels = ax.transData.transform(np.array([[float(r["sigma"]), float(r["N"])] for r in rows]))
    places = {r["row_id"]: {"x": round(float(x), 1), "y": round(height - float(y), 1)} for r, (x, y) in zip(rows, pixels)}
    save(fig, f"search_{year}{'_mobile' if mobile else ''}.svg")
    return places


def panels(kind, winners, mobile, fresh=None):
    """The 44 annual fits, the 44 selected parameter values, or the fits with new draws."""
    years = np.array([int(w["year"]) for w in winners])
    count = 4 if kind == "parameters" else 3
    width = 420 if mobile else 1200
    height = (1280 if kind == "parameters" else 1090) if mobile else (1080 if kind == "parameters" else 990)
    tick, label = (17, 17) if mobile else (19, 21)
    fig, axes = plt.subplots(count, 1, figsize=(width / 72, height / 72), dpi=72, facecolor="white")
    # On a narrow screen the legend takes one line per entry; the fresh-draw figure has three.
    top = (.88 if kind == "fresh" else .9) if mobile else .925
    fig.subplots_adjust(left=.22 if mobile else .1, right=.96, top=top, bottom=.065, hspace=.5 if mobile else .4)
    for ax in axes:
        style(ax, tick)
        ax.set_xlim(1980, 2023)
        ax.set_xticks([1980, 2000, 2023] if mobile else [1980, 1990, 2000, 2010, 2023])
        ax.yaxis.set_major_locator(MaxNLocator(4))
    if kind == "parameters":
        series = (("sigma", "Dispersion σ", 1), ("N", "Potential firms N", 1),
                  ("zeta", "Fixed-cost control ζ", 1), ("phi", "Fixed labor φ\n(millionths)", 1e6))
        for ax, (key, name, scale) in zip(axes, series):
            ax.plot(years, [float(w[key]) * scale for w in winners], color=BLUE, linewidth=2.1)
            if key == "N":
                ax.step(years, [int(w["M"]) for w in winners], where="mid", color=COPPER,
                        linewidth=1.5, linestyle="--", label="M = floor(N)")
                ax.legend(frameon=False, fontsize=tick, loc="best")
            ax.set_ylabel(name, fontsize=label, color=INK, labelpad=8)
    else:
        names = ("Reallocation (%)", "Markup", "SGA / cost (%)") if mobile else \
                ("Reallocation (%)", "Sales-weighted markup", "SGA / total cost (%)")
        for k, ax in enumerate(axes):
            ax.plot(years, [float(w[f"target_{MOMENTS[k]}"]) * SCALES[k] for w in winners],
                    color=INK, linewidth=2.1, label="Data", zorder=4)
            if kind == "fit":
                ax.plot(years, [float(w[MOMENTS[k]]) * SCALES[k] for w in winners],
                        color=BLUE, linewidth=2.1, label="Model at the year's best candidate", zorder=3)
            else:
                draws = np.array([[float(r[MOMENTS[k]]) for r in fresh[w["year"]]] for w in winners]) * SCALES[k]
                ax.plot(years, draws.mean(axis=1), color=BLUE, linewidth=2.1,
                        label="Model, mean of three new draws", zorder=3)
                ax.fill_between(years, draws.min(axis=1), draws.max(axis=1), color=BLUE, alpha=.2,
                                linewidth=0, label="Range of the three draws", zorder=2)
            ax.set_ylabel(names[k], fontsize=label, color=INK, labelpad=8)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper left", frameon=False, fontsize=tick,
                   ncol=1 if mobile else len(handles), bbox_to_anchor=(.2 if mobile else .085, .995))
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)
    axes[-1].set_xlabel("Year", fontsize=label, color=INK)
    stem = {"fit": "annual_fit", "parameters": "annual_parameters", "fresh": "fresh_draws"}[kind]
    save(fig, f"{stem}{'_mobile' if mobile else ''}.svg")


def main():
    script = ASSETS / "gallery_data.js"
    raw = script.read_text(encoding="utf-8")
    start, end = raw.index("{"), raw.rindex("}") + 1
    data = json.loads(raw[start:end])
    candidates = {}
    for row in read_rows("search_results.csv"):
        candidates.setdefault(row["year"], []).append(row)
    moved = 0
    for year, saved in data["years"].items():
        rows = candidates[year]
        assert len(rows) == len(saved["candidates"]) == 512, year
        wide, narrow = scatter(year, rows, saved["box"], False), scatter(year, rows, saved["box"], True)
        for mobile, mode in ((False, "desktop"), (True, "mobile")):
            saved["scatter"][mode]["width"], saved["scatter"][mode]["height"] = SCATTER[mobile]
        for candidate in saved["candidates"]:
            row_id = str(candidate["row_id"])
            candidate["point"] = {"desktop": wide[row_id], "mobile": narrow[row_id]}
            moved += 1
    winners = sorted(read_rows("annual_parameters.csv"), key=lambda w: int(w["year"]))
    assert len(winners) == 44
    fresh = {}
    for row in read_rows("fresh_draws.csv"):
        fresh.setdefault(row["year"], []).append(row)
    assert sorted(fresh) == [w["year"] for w in winners] and all(len(rows) == 3 for rows in fresh.values())
    for kind in ("fit", "parameters", "fresh"):
        for mobile in (False, True):
            panels(kind, winners, mobile, fresh)
    # Root mean squared error over the 44 years and three draws, in the page's units.
    errors = [np.sqrt(np.mean([(float(r[name]) - float(w[f"target_{name}"])) ** 2
                               for w in winners for r in fresh[w["year"]]])) for name in MOMENTS]
    data["summary"].pop("fixed_phi", None)
    data["summary"].pop("stability", None)
    data["meta"].pop("stability_note", None)
    data["summary"]["fresh_draws"] = {"reallocation_rmse": f"{100 * errors[0]:.3f} pp",
                                      "markup_rmse": f"{errors[1]:.5f}", "sga_rmse": f"{100 * errors[2]:.3f} pp"}
    script.write_text(raw[:start] + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + raw[end:],
                      encoding="utf-8")
    print(f"Drew {2 * len(data['years'])} scatter plots and 6 annual figures; moved {moved} candidate points.")
    print("Fit with three new draws (RMSE): " + ", ".join(data["summary"]["fresh_draws"].values()))


if __name__ == "__main__":
    main()
