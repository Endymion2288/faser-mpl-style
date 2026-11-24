"""2D detector efficiency (faser_bird) and calorimeter density (viridis) heatmaps.

Inspired by arXiv:2504.13008 (efficiency_complete_250402),
arXiv:2602.17575 (Angle2D_FASER), and arXiv:2412.03186 (geo_bgr_radius_momentum_hist).
Demonstrates: plot_2d, ROOT kBird replica ('faser_bird'), perceptual 'viridis'
with logz=True zero masking, and unobstructed loc='outside' transparent logo branding.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import faser_mpl_style as fms


def make_plots(output_dir: Path, show: bool = False) -> list[Path]:
    """Build and save both 2D heatmap showcase figures."""
    if not show:
        plt.switch_backend("Agg")

    fms.use_faser_style("faser")
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    # 1. Detector tracking efficiency map using ROOT kBird replica ('faser_bird')
    xbins = np.linspace(-110.0, 110.0, 45)
    ybins = np.linspace(-110.0, 110.0, 45)
    xc = 0.5 * (xbins[:-1] + xbins[1:])
    yc = 0.5 * (ybins[:-1] + ybins[1:])
    xx, yy = np.meshgrid(xc, yc)
    rr = np.hypot(xx, yy)

    # Smooth plateau efficiency inside the 100 mm circular magnet aperture + module gap
    eff = 0.985 / (1.0 + np.exp((rr - 96.0) / 3.8))
    gap_dip = 0.10 * np.exp(-((yy - 0.0) / 4.5) ** 2) * (rr < 95.0)
    eff = np.clip(eff - gap_dip, 0.0, 1.0)
    eff = np.where(rr > 106.0, np.nan, eff)

    fig1, ax1 = plt.subplots()
    fms.plot_2d(
        xbins,
        ybins,
        eff,
        cmap="faser_bird",
        vmin=0.0,
        vmax=1.0,
        zlabel="Tracking Efficiency",
        ax=ax1,
    )
    ax1.set_aspect("equal", adjustable="box")
    fms.set_xlabel(r"$x$ [mm]", ax=ax1)
    fms.set_ylabel(r"$y$ [mm]", ax=ax1)
    fms.draw_faser_logo(
        ax=ax1,
        width=0.22,
        loc="outside",
        status="Simulation",
        com=13.6,
    )

    out1 = output_dir / "03a_detector_efficiency_bird.png"
    fig1.savefig(out1)
    saved.append(out1)
    if show:
        plt.show()
    plt.close(fig1)

    # 2. Calorimeter radial distance vs muon momentum using 'viridis' + logz=True
    rng = np.random.default_rng(202412)
    n_events = 35_000
    log_p = rng.normal(loc=2.55, scale=0.45, size=n_events)
    p_mu = 10.0**log_p
    # Higher-momentum muons stay closer to the beam axis (smaller r)
    r_mean = 22.0 + 95.0 / (1.0 + p_mu / 220.0)
    radius = np.abs(rng.normal(loc=r_mean, scale=22.0))

    p_bins = np.geomspace(20.0, 3000.0, 41)
    r_bins = np.linspace(0.0, 140.0, 36)
    hist2d, _, _ = np.histogram2d(p_mu, radius, bins=[p_bins, r_bins])

    fig2, ax2 = plt.subplots()
    fms.plot_2d(
        p_bins,
        r_bins,
        hist2d.T,
        cmap="viridis",
        logz=True,
        zlabel="Events / bin",
        ax=ax2,
    )
    ax2.set_xscale("log")
    fms.set_xlabel(r"Muon Momentum $p_\mu$ [GeV]", ax=ax2)
    fms.set_ylabel(r"Transverse Radius $r$ [mm]", ax=ax2)
    fms.draw_faser_logo(
        ax=ax2,
        width=0.22,
        loc="outside",
        com=13.6,
        lumi=65.6,
    )

    out2 = output_dir / "03b_calo_radius_momentum_viridis.png"
    fig2.savefig(out2)
    saved.append(out2)
    if show:
        plt.show()
    plt.close(fig2)

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
