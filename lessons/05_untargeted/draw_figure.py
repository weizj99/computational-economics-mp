"""Three panels of the cumulated markup decomposition: data, model, model moved.

Lines are centred five-year moving averages of the levels. The third panel
shifts the model so that its total starts at the data's 1980 value. Short ticks
under the model panels mark the years whose firms are new draws.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager
import matplotlib.pyplot as plt

FONTS = Path(__file__).resolve().parents[2] / "06_teaching/assets/fonts"
INK, MUTED, LINE = "#20242b", "#59636e", "#dce1e6"
SERIES = (  # (part, label, colour, width): the total is the sum of the other three
    ("total", "Total", INK, 2.6),
    ("reallocation", "Reallocation", "#2357a4", 2.0),
    ("net_entry", "Net entry", "#1a9a86", 2.0),
    ("within", "Within firms", "#a85b2a", 2.0),
)
PANELS = (("data_{}_ma", "Data"), ("model_{}_ma", "Model"),
          ("moved_model_{}_ma", "Model, moved to the data’s 1980 level"))


def _font():
    for ttf in sorted(FONTS.glob("*.ttf")):
        font_manager.fontManager.addfont(str(ttf))
    names = {font_manager.FontProperties(fname=str(ttf)).get_name() for ttf in FONTS.glob("*.ttf")}
    return "Source Sans 3" if "Source Sans 3" in names else "sans-serif"


def _panel(ax, rows, column, title, label_lines, new_draw_ticks, size, weight):
    years = [row["year"] for row in rows]
    ends = []
    for part, label, colour, width in SERIES:
        values = [row[column.format(part)] for row in rows]
        ax.plot(years, values, color=colour, linewidth=width, solid_capstyle="round", zorder=3 if part == "total" else 2)
        ends.append((values[-1], label, colour))
    ax.set_title(title, loc="left", fontsize=size, fontweight=weight, color=INK, pad=10)
    ax.set_xlim(1980, 2023)
    ax.set_ylim(1.15, 1.70)
    ax.set_xticks([1980, 1990, 2000, 2010, 2020])
    ax.grid(axis="y", color=LINE, linewidth=1)
    ax.tick_params(colors=MUTED, labelsize=size - 2, length=0, pad=6)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#aeb8c2")
    if new_draw_ticks:
        for year in new_draw_ticks:
            ax.plot([year, year], [1.152, 1.168], color=MUTED, linewidth=1.2, zorder=1)
    if label_lines:
        # Direct labels at the line ends, nudged apart so they never overlap.
        placed = []
        for value, label, colour in sorted(ends, key=lambda item: item[0]):
            y = max(value, placed[-1] + 0.03) if placed else value
            placed.append(y)
            ax.annotate(label, (2023, value), xytext=(2024.2, y), textcoords="data",
                        fontsize=size - 2, color=INK, va="center", annotation_clip=False)
            ax.plot([2023.2, 2024], [value, y], color=colour, linewidth=1, clip_on=False)


def _figure(rows, path, layout):
    family = _font()
    # The fallback font has no semibold, so use bold rather than warn.
    weight = 600 if family == "Source Sans 3" else "bold"
    # Glyphs become paths, so an <img> shows the course font without loading it.
    # A fixed salt keeps the SVG element ids, and so the whole file, the same on every run.
    plt.rcParams.update({"font.family": family, "svg.fonttype": "path", "svg.hashsalt": "unit05",
                         "axes.facecolor": "white"})
    new_draws = [row["year"] for row in rows[1:] if not row["same_firms_as_previous_year"]]
    if layout == "wide":
        fig, axes = plt.subplots(1, 3, figsize=(1160 / 72, 470 / 72), sharey=True)
        fig.subplots_adjust(left=0.05, right=0.9, top=0.84, bottom=0.12, wspace=0.12)
        size = 17
    else:
        fig, axes = plt.subplots(3, 1, figsize=(350 / 72, 1110 / 72), sharey=True)
        fig.subplots_adjust(left=0.14, right=0.72, top=0.955, bottom=0.075, hspace=0.32)
        size = 15
    for i, (ax, (column, title)) in enumerate(zip(axes, PANELS)):
        _panel(ax, rows, column, title, label_lines=(layout != "wide" or i == 2),
               new_draw_ticks=new_draws if i > 0 else None, size=size, weight=weight)
    handles = [plt.Line2D([], [], color=colour, linewidth=width) for _, _, colour, width in SERIES]
    labels = [label for _, label, _, _ in SERIES]
    handles.append(plt.Line2D([], [], color=MUTED, linewidth=1.2, marker="|", markersize=10, linestyle="none"))
    labels.append("Year with new draws")
    if layout == "wide":
        fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.05, 1.0), ncol=5,
                   frameon=False, fontsize=size - 2, labelcolor=INK, handlelength=1.6, columnspacing=1.6)
    else:
        fig.legend(handles[-1:], labels[-1:], loc="lower left", bbox_to_anchor=(0.14, 0.0),
                   frameon=False, fontsize=size - 2, labelcolor=INK, handlelength=1.2)
    fig.savefig(path, format="svg", metadata={"Date": None})
    plt.close(fig)


def draw(rows, output_dir):
    """Write the wide and the narrow figure as SVG files."""
    output_dir = Path(output_dir)
    _figure(rows, output_dir / "markup_decomposition.svg", "wide")
    _figure(rows, output_dir / "markup_decomposition_mobile.svg", "narrow")
