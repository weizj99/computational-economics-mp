"""Draw the home page's figure: the sales-weighted markup, data and model, 1980-2023.

It reads unit 03's saved annual winners (annual_parameters.csv) and writes
website/assets/home_markup.svg for wide screens and home_markup_mobile.svg for
narrow ones, in the course's type and colours. The page gives the caption.

    python tools/site/home_figure.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "website/modules/03_estimation/assets/annual_parameters.csv"
OUTPUT = ROOT / "website/assets"
FONTS = ROOT / "website/assets/fonts"
INK, MUTED, BLUE, GRID, AXIS = "#20242b", "#59636e", "#2357a4", "#e3e7eb", "#aab4bd"

for name in ("SourceSans3-Regular.ttf", "SourceSans3-Semibold.ttf"):
    font_manager.fontManager.addfont(FONTS / name)
plt.rcParams.update({"font.family": "Source Sans 3", "svg.fonttype": "path", "svg.hashsalt": "home",
                     "axes.unicode_minus": True, "savefig.pad_inches": .05})


def draw(rows, width, height, mobile):
    years = [int(r["year"]) for r in rows]
    data = [float(r["target_markup_sales_weighted"]) for r in rows]
    model = [float(r["markup_sales_weighted"]) for r in rows]
    size = 15 if mobile else 16
    fig = plt.figure(figsize=(width / 72, height / 72), dpi=72, facecolor="white")
    ax = fig.add_axes([.14, .12, .79, .84] if mobile else [.12, .11, .82, .85])
    ax.plot(years, data, color=INK, linewidth=2.2, zorder=3)
    ax.plot(years, model, color=BLUE, linewidth=2.2, zorder=2)
    # Label the lines where they are furthest apart, at the start.
    ax.text(1981.2, data[0] - .035, "Data", color=INK, fontsize=size, va="top", fontweight=600)
    ax.text(1981.2, model[0] + .025, "Model", color=BLUE, fontsize=size, va="bottom", fontweight=600)
    ax.set_xlim(1980, 2023)
    ax.set_ylim(1.1, 1.7)
    ax.set_xticks([1980, 2000, 2023])
    ax.set_yticks([1.2, 1.4, 1.6])
    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=size, length=4)
    ax.grid(axis="y", color=GRID, linewidth=.8)
    ax.set_axisbelow(True)
    name = f"home_markup{'_mobile' if mobile else ''}.svg"
    fig.savefig(OUTPUT / name, format="svg", dpi=72, facecolor="white", metadata={"Date": None})
    plt.close(fig)
    return name


def main():
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        rows = sorted(csv.DictReader(stream), key=lambda r: int(r["year"]))
    assert len(rows) == 44
    names = [draw(rows, 480, 330, False), draw(rows, 350, 280, True)]
    print("Wrote " + " and ".join(names))


if __name__ == "__main__":
    main()
