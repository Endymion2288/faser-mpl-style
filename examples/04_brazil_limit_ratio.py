"""1D 95% CL upper limit Brazil band with signal-strength ratio panel.

Inspired by arXiv:2607.26195 (ratio_lambda1p0e4).
Demonstrates: ratio_axes, plot_limit (FASER Brazil bands), plot_band (theory
uncertainty), plot_ratio, draw_faser_logo, set_xlabel, and set_ylabel.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import faser_mpl_style as fms


def make_plot(output_dir: Path, show: bool = False) -> Path:
    """Build and save the 1D Brazil-band upper limit + ratio figure."""
    if not show:
        plt.switch_backend("Agg")

    fms.use_faser_style("faser")

    masses = np.array([200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200], dtype=float)

    # Smooth expected cross-section limit [fb] and realistic ±1σ / ±2σ bands
    expected = 12.0 * (masses / 500.0) ** (-0.55) + 1.8 * np.exp((masses - 950.0) / 300.0)
    one_lo = expected * 0.72
    one_hi = expected * 1.42
    two_lo = expected * 0.54
    two_hi = expected * 1.98

    # Mild statistical fluctuation in observed 95% CL limit
    fluct = np.array([1.06, 0.94, 1.12, 1.03, 0.89, 0.96, 1.14, 1.08, 0.92, 1.01, 1.05])
    observed = expected * fluct

    # Steeply falling theory cross-section curve with ±15% scale/PDF uncertainty
    theory = 650.0 * np.exp(-masses / 210.0)
    theory_err = 0.15 * theory

    fig, ax, ax_r = fms.ratio_axes()

    fms.plot_limit(
        masses,
        expected,
        observed=observed,
        one_sigma=(one_lo, one_hi),
        two_sigma=(two_lo, two_hi),
        band_palette="faser",
        ax=ax,
    )

    ax.plot(
        masses,
        theory,
        color="faser:purple",
        linewidth=2.0,
        label=r"Theory ($\Lambda = 10\ \mathrm{keV}$)",
        zorder=4,
    )
    fms.plot_band(
        masses,
        theory - theory_err,
        theory + theory_err,
        color="faser:purple",
        alpha=0.25,
        ax=ax,
    )

    ax.set_yscale("log")
    ax.set_xlim(180.0, 1220.0)
    ax.set_ylim(0.5, 5.0e3)

    # Lower ratio panel: observed limit / expected limit (signal-strength sensitivity check)
    fms.plot_ratio(
        masses,
        observed,
        expected,
        den_err=0.5 * (one_hi - one_lo),
        mode="ratio",
        ylim=(0.4, 1.8),
        ylabel="Obs. / Exp.",
        band_color="faser:onesigma",
        band_style="fill",
        ax=ax_r,
    )

    fms.draw_faser_logo(
        ax=ax,
        width=0.22,
        loc="upper left",
        com=13.6,
        lumi=186,
        desc=r"Quirk Search ($\Lambda = 10\ \mathrm{keV}$)",
        layout="stacked",
    )
    ax.legend(loc="upper right", ncol=1)

    fms.set_xlabel(r"Quirk Mass $m_Q$ [GeV]", ax=ax)
    fms.set_ylabel(r"95% CL Upper Limit on $\sigma$ [fb]", ax=ax)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "04_brazil_limit_ratio.png"
    fig.savefig(out_path)
    if show:
        plt.show()
    plt.close(fig)
    return out_path


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
    out_path = make_plot(args.output_dir, show=args.show)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
