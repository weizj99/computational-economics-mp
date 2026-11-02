"""Draw the image that link previews show for the course, 1200 x 627 pixels.

The home page names it in its og:image tag, so LinkedIn and other sites show
it with the page title. It says what the course is and shows the path through
it: equilibrium, estimation, acceleration. It uses the course's type and
colours and writes website/assets/social-preview.png.

    python tools/site/social_preview.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "website/assets/social-preview.png"
FONTS = ROOT / "website/assets/fonts"
WIDTH, HEIGHT, DPI = 1200, 627, 100
NAVY, MUTED, BLUE, PAPER, CARD, EDGE = "#1c2e45", "#4f5b68", "#2357a4", "#eef2f6", "#ffffff", "#d6dee7"
LEFT, RIGHT = 64, WIDTH - 64

for name in ("SourceSans3-Regular.ttf", "SourceSans3-Semibold.ttf"):
    font_manager.fontManager.addfont(FONTS / name)
plt.rcParams.update({"font.family": "Source Sans 3"})


def pt(px):
    """Font size in points for a height in pixels at the figure's resolution."""
    return px * 72 / DPI


def text(ax, x, y, s, size, color, weight="normal", ha="left"):
    ax.text(x, y, s, fontsize=pt(size), color=color, fontweight=weight, ha=ha, va="center")


def sigma(ax, cx, cy):
    text(ax, cx, cy - 2, "Σ", 58, BLUE, "semibold", "center")


def chart(ax, cx, cy):
    """Rising bars with a trend line: fitting a model to data."""
    left, base = cx - 26, cy + 22
    for i, h in enumerate((14, 22, 30, 40)):
        ax.add_patch(Rectangle((left + i * 14, base - h), 8, h, color=BLUE, alpha=.35, lw=0))
    ax.plot([left - 2, left + 18, left + 32, left + 52], [base - 10, base - 22, base - 26, base - 44],
            color=BLUE, lw=3.2, solid_capstyle="round", solid_joinstyle="round")
    ax.add_patch(Polygon([(left + 56, base - 49), (left + 44, base - 46), (left + 53, base - 37)], color=BLUE, lw=0))


def chip(ax, cx, cy):
    """A processor: the computation itself."""
    ax.add_patch(FancyBboxPatch((cx - 19, cy - 19), 38, 38, boxstyle="round,pad=0,rounding_size=6",
                                fill=False, ec=BLUE, lw=3.2))
    ax.add_patch(Rectangle((cx - 8, cy - 8), 16, 16, fill=False, ec=BLUE, lw=2.6))
    for offset in (-10, 0, 10):
        for x0, y0, x1, y1 in ((cx + offset, cy - 19, cx + offset, cy - 28), (cx + offset, cy + 19, cx + offset, cy + 28),
                               (cx - 19, cy + offset, cx - 28, cy + offset), (cx + 19, cy + offset, cx + 28, cy + offset)):
            ax.plot([x0, x1], [y0, y1], color=BLUE, lw=2.6, solid_capstyle="round")


def main():
    fig = plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI, facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(HEIGHT, 0)
    ax.axis("off")
    text(ax, LEFT, 88, "AN INTERACTIVE PYTHON COURSE", 24, MUTED, "semibold")
    text(ax, LEFT, 158, "Computational Economics", 72, NAVY, "semibold")
    text(ax, LEFT, 234, "From economic models to estimation and fast computation.", 35, MUTED)
    gap, top, height = 72, 292, 168
    width = (RIGHT - LEFT - 2 * gap) / 3
    for i, (label, icon) in enumerate((("Equilibrium", sigma), ("Estimation", chart), ("Acceleration", chip))):
        x = LEFT + i * (width + gap)
        ax.add_patch(FancyBboxPatch((x, top + 4), width, height, boxstyle="round,pad=0,rounding_size=18",
                                    fc="#000000", alpha=.05, lw=0))
        ax.add_patch(FancyBboxPatch((x, top), width, height, boxstyle="round,pad=0,rounding_size=18",
                                    fc=CARD, ec=EDGE, lw=1.5))
        icon(ax, x + width / 2, top + 62)
        text(ax, x + width / 2, top + 122, label, 34, NAVY, ha="center")
        if i < 2:
            text(ax, x + width + gap / 2, top + height / 2, "→", 36, MUTED, ha="center")
    text(ax, LEFT, 540, "Interactive lessons · Videos · Open-source Python code", 25, MUTED)
    # Save without an alpha channel: the image is opaque, and some sites
    # draw transparent PNGs on their own background colour.
    fig.canvas.draw()
    Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:, :, :3]).save(OUTPUT, optimize=True)
    plt.close(fig)
    print("wrote", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
