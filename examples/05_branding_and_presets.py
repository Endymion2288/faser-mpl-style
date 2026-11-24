"""Visual catalog of FASER style presets, palettes, and transparent branding modes.

Demonstrates:
  1. All 8 curated discrete color palettes in FASER_PALETTES.
  2. Transparent RGBA draw_faser_logo color tinting ('black', 'white',
     'faser:blue', 'faser:red') over light, dark, and colored backgrounds.
  3. Typographic draw_faser_label vs graphical draw_faser_logo ('stacked',
     'inline', and 'outside' placements).
  4. Side-by-side comparison of all 4 presets ('faser', 'faser-square',
     'faser-talk', 'faser-atlas-compat') rendered via style_context.
"""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

import faser_mpl_style as fms


def _render_preset_to_rgba(preset: str) -> np.ndarray:
    """Render a standardized sample physics curve in `preset` to an RGBA array."""
    x = np.linspace(0.0, 10.0, 200)
    y1 = 0.75 * np.exp(-0.35 * x) * np.cos(1.4 * x) + 1.05
    y2 = 0.65 * np.exp(-0.22 * x) + 0.30

    with fms.style_context(preset):
        fig, ax = plt.subplots()
        ax.plot(x, y1, label="Signal")
        ax.plot(x, y2, linestyle="--", label="Bkg.")
        ax.set_xlim(0.0, 10.0)
        ax.set_ylim(0.0, 2.7)
        ax.set_xlabel(r"$E_{\mathrm{vis}}$ [TeV]")
        ax.set_ylabel("Normalized Yield")
        ax.legend(loc="upper right")
        fms.draw_faser_label(
            ax=ax,
            status="Sim.",
            desc=preset,
            loc="upper left",
        )
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return mpimg.imread(buf)


def make_plots(output_dir: Path, show: bool = False) -> list[Path]:
    """Generate the palettes/branding catalog and the 4-preset comparison sheet."""
    if not show:
        plt.switch_backend("Agg")

    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    # Figure A: Palettes + Transparent Logo Tinting + Branding Modes (2x2)
    fms.use_faser_style("faser")
    fig_a, axes = plt.subplots(2, 2, figsize=(13.5, 9.5))
    fig_a.subplots_adjust(left=0.07, right=0.97, bottom=0.06, top=0.92, wspace=0.22, hspace=0.34)

    # Panel (0, 0): All 8 discrete palettes
    ax_pal = axes[0, 0]
    palette_names = list(fms.FASER_PALETTES.keys())
    n_pals = len(palette_names)
    for row_idx, name in enumerate(palette_names):
        y_pos = n_pals - 1 - row_idx
        colors = fms.FASER_PALETTES[name]
        ax_pal.text(-0.25, y_pos + 0.36, name, ha="right", va="center", fontsize=11, fontweight="bold")
        for col_idx, hex_col in enumerate(colors):
            rect = mpatches.Rectangle(
                (col_idx, y_pos + 0.08),
                0.86,
                0.56,
                facecolor=hex_col,
                edgecolor="#333333",
                linewidth=0.6,
            )
            ax_pal.add_patch(rect)
    ax_pal.set_xlim(-3.2, 10.2)
    ax_pal.set_ylim(-0.2, n_pals + 0.2)
    ax_pal.set_axis_off()
    ax_pal.set_title("Curated FASER Color Palettes", loc="left", fontsize=14, fontweight="bold")

    # Panel (0, 1): Transparent RGBA logo color tinting on colored / dark backgrounds
    ax_tint = axes[0, 1]
    grad = np.linspace(0.0, 1.0, 256).reshape(1, -1)
    ax_tint.imshow(
        grad,
        aspect="auto",
        cmap="viridis",
        extent=(0.0, 1.0, 0.50, 1.0),
        origin="lower",
    )
    ax_tint.add_patch(mpatches.Rectangle((0.0, 0.0), 0.5, 0.50, facecolor="#F5F7FA", edgecolor="none"))
    ax_tint.add_patch(mpatches.Rectangle((0.5, 0.0), 0.5, 0.50, facecolor="#1B263B", edgecolor="none"))
    ax_tint.set_xlim(0.0, 1.0)
    ax_tint.set_ylim(0.0, 1.0)
    ax_tint.set_xticks([])
    ax_tint.set_yticks([])

    fms.draw_faser_logo(x=0.06, y=0.90, ax=ax_tint, width=0.38, color="white", loc="upper left")
    fms.draw_faser_logo(x=0.94, y=0.90, ax=ax_tint, width=0.38, color="black", loc="upper right")
    fms.draw_faser_logo(x=0.06, y=0.38, ax=ax_tint, width=0.38, color="faser:blue", loc="upper left")
    fms.draw_faser_logo(x=0.94, y=0.38, ax=ax_tint, width=0.38, color="faser:onesigma", loc="upper right")
    ax_tint.text(0.06, 0.55, 'color="white" on viridis', color="white", fontsize=10, ha="left")
    ax_tint.text(0.94, 0.55, 'color="black" on viridis', color="black", fontsize=10, ha="right")
    ax_tint.text(0.06, 0.07, 'color="faser:blue"', color="faser:blue", fontsize=10, ha="left")
    ax_tint.text(0.94, 0.07, 'color="faser:onesigma"', color="faser:onesigma", fontsize=10, ha="right")
    ax_tint.set_title("Transparent RGBA Logo Tinting (Zero White Box)", loc="left", fontsize=14, fontweight="bold")

    # Panel (1, 0): Typographic draw_faser_label showcase (inside + outside)
    ax_txt = axes[1, 0]
    ax_txt.set_xlim(0.0, 1.0)
    ax_txt.set_ylim(0.0, 1.0)
    ax_txt.set_xticks([])
    ax_txt.set_yticks([])
    fms.draw_faser_label(
        ax=ax_txt,
        experiment="FASER",
        status="Preliminary",
        com=13.6,
        lumi=65.6,
        loc="outside",
        fontsize=13,
    )
    fms.draw_faser_label(
        ax=ax_txt,
        experiment="FASERν",
        status="sim_prelim",
        com=13.6,
        lumi=186,
        desc="Typographic inside stamp",
        loc="upper left",
        fontsize=13,
    )
    fms.draw_faser_label(
        ax=ax_txt,
        experiment="FASER2",
        status="wip",
        com=14,
        lumi="3 ab$^{-1}$",
        desc="HL-LHC Forward Physics Facility",
        loc="lower right",
        fontsize=12,
    )

    # Panel (1, 1): Graphical draw_faser_logo layouts ('outside', 'stacked', 'inline')
    ax_logo = axes[1, 1]
    ax_logo.set_xlim(0.0, 1.0)
    ax_logo.set_ylim(0.0, 1.0)
    ax_logo.set_xticks([])
    ax_logo.set_yticks([])
    fms.draw_faser_logo(
        ax=ax_logo,
        width=0.26,
        loc="outside",
        com=13.6,
        lumi=65.6,
        fontsize=12,
    )
    fms.draw_faser_logo(
        ax=ax_logo,
        width=0.30,
        loc="upper left",
        status="Simulation",
        com=13.6,
        lumi=186,
        desc='layout="stacked"',
        layout="stacked",
        fontsize=11,
    )
    fms.draw_faser_logo(
        ax=ax_logo,
        width=0.28,
        loc="lower left",
        status="Preliminary",
        desc='layout="inline"',
        layout="inline",
        fontsize=11,
    )

    out_a = output_dir / "05a_palettes_and_branding.png"
    fig_a.savefig(out_a)
    saved.append(out_a)
    if show:
        plt.show()
    plt.close(fig_a)

    # Figure B: 2x2 gallery comparing all 4 style presets rendered in their native style_context
    preset_imgs = [(preset, _render_preset_to_rgba(preset)) for preset in fms.STYLES]
    fig_b, axes_b = plt.subplots(2, 2, figsize=(13.0, 10.8))
    fig_b.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.90, wspace=0.08, hspace=0.16)
    fig_b.suptitle("faser-mpl-style Preset Comparison", fontsize=18, fontweight="bold", y=0.97)

    for ax_p, (preset, img) in zip(axes_b.flat, preset_imgs):
        ax_p.imshow(img)
        ax_p.set_title(f'style_context("{preset}")', fontsize=14, fontweight="bold", pad=6)
        ax_p.set_axis_off()

    out_b = output_dir / "05b_presets_comparison.png"
    fig_b.savefig(out_b, dpi=200)
    saved.append(out_b)
    if show:
        plt.show()
    plt.close(fig_b)

    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to write rendered PNG figures.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display figures interactively instead of using the Agg backend.",
    )
    args = parser.parse_args()
    for path in make_plots(args.output_dir, show=args.show):
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
