"""FASERν calorimeter neutrino energy spectrum with stacked MC, data, and ratio panel.

Inspired by arXiv:2410.10363 (calo_region_flav) and arXiv:2412.03186.
Demonstrates: ratio_axes, plot_mc_stack, plot_data, poisson_errors, plot_ratio,
draw_faser_label (typographic FASERν), set_xlabel, and set_ylabel.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import faser_mpl_style as fms


def make_plot(output_dir: Path, show: bool = False) -> Path:
    """Build and save the FASERν neutrino energy spectrum figure."""
    if not show:
        plt.switch_backend("Agg")

    fms.use_faser_style("faser")

    rng = np.random.default_rng(202410)
    bins = np.linspace(100.0, 1500.0, 15)
    centers = 0.5 * (bins[:-1] + bins[1:])

    # Realistic smoothly falling forward neutrino calorimeter energy spectra
    numu_cc = 95.0 * (centers / 250.0) ** 1.15 * np.exp(-centers / 260.0)
    nue_cc = 28.0 * (centers / 280.0) ** 1.25 * np.exp(-centers / 290.0)
    nc_nutau = 14.0 * (centers / 220.0) ** 0.90 * np.exp(-centers / 240.0)
    hadron_bkg = 9.0 * np.exp(-centers / 190.0)

    hists = [numu_cc, nue_cc, nc_nutau, hadron_bkg]
    labels = [
        r"$\nu_\mu + \bar{\nu}_\mu$ CC",
        r"$\nu_e + \bar{\nu}_e$ CC",
        r"NC + $\nu_\tau$ CC",
        "Neutral hadrons",
    ]
    # Per-component relative systematic + MC statistical uncertainties
    rel_errs = [0.12, 0.15, 0.20, 0.30]
    yerrs = [np.sqrt(h + (r * h) ** 2) for h, r in zip(hists, rel_errs)]

    total_expected = np.sum(hists, axis=0)
    data = rng.poisson(total_expected * 1.02).astype(float)

    fig, ax, ax_r = fms.ratio_axes()

    total, total_err = fms.plot_mc_stack(
        bins,
        hists,
        labels=labels,
        yerr=yerrs,
        err_label=r"MC Stat. $\oplus$ Syst.",
        err_style="hatch",
        ax=ax,
    )
    fms.plot_data(bins, data, yerr="poisson", label="Data", ax=ax)

    fms.plot_ratio(
        bins,
        data,
        total,
        num_err=fms.poisson_errors(data),
        den_err=total_err,
        mode="ratio",
        ylim=(0.45, 1.55),
        ylabel="Data / MC",
        ax=ax_r,
    )

    ax.set_ylim(bottom=0.0)
    fms.draw_faser_label(
        ax=ax,
        experiment="FASERν",
        status="Preliminary",
        com=13.6,
        lumi=65.6,
        desc="Calorimeter Region",
        loc="upper left",
        pad_y=0.38,
    )
    ax.legend(loc="upper right")

    fms.set_xlabel(r"$E_{\mathrm{cal}}$ [GeV]", ax=ax)
    fms.set_ylabel("Events / 100 GeV", ax=ax)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "01_neutrino_spectrum_ratio.png"
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
