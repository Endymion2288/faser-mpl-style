"""2D Dark Photon exclusion contour in canonical FASER publication style.

Inspired by arXiv:2308.05587 (FASER_LimitContour90CL_BL_Final) and
arXiv:2611.03904 (FASER_LimitContourX17_ModelA).
Demonstrates: plot_exclusion (existing gray constraints, dashed expected +
signature #B9FF61 ±1σ band, vivid #0033FF hatched observed contour) and
transparent draw_faser_logo inside axes.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import faser_mpl_style as fms


def _beam_dump_lobe(
    m_min: float,
    m_max: float,
    eps_center: float,
    log_half_height: float,
    tilt: float = -0.35,
    n_pts: int = 120,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a smooth closed beam-dump exclusion polygon in (m_A', epsilon)."""
    theta = np.linspace(0.0, 2.0 * np.pi, n_pts, endpoint=True)
    log_m_lo, log_m_hi = np.log10(m_min), np.log10(m_max)
    log_m_mid = 0.5 * (log_m_lo + log_m_hi)
    log_m_rad = 0.5 * (log_m_hi - log_m_lo)

    u = np.cos(theta)
    v = np.sin(theta)
    # Slight asymmetry typical of forward decay-volume acceptance
    log_m = log_m_mid + log_m_rad * (u + 0.12 * (1.0 - u**2))
    taper = np.clip(1.0 - 0.35 * u, 0.55, 1.35)
    log_eps = (
        np.log10(eps_center)
        + tilt * (log_m - log_m_mid)
        + log_half_height * v * taper
    )
    return 10.0**log_m, 10.0**log_eps


def make_plot(output_dir: Path, show: bool = False) -> Path:
    """Build and save the 2D dark-photon exclusion contour figure."""
    if not show:
        plt.switch_backend("Agg")

    fms.use_faser_style("faser")

    fig, ax = plt.subplots()
    ax.set_xscale("log")
    ax.set_yscale("log")

    # Existing experimental bounds (illustrative shapes modeled after 2308.05587)
    m_na64 = np.geomspace(0.008, 0.036, 80)
    y_na64 = 1.7e-4 * (m_na64 / 0.008) ** 0.65

    m_babar = np.geomspace(0.036, 0.80, 90)
    y_babar = 6.5e-4 * np.ones_like(m_babar)

    m_kloe = np.geomspace(0.070, 0.72, 80)
    y_kloe = 1.15e-3 * (1.0 + 0.14 * np.sin(8.0 * np.log10(m_kloe / 0.07)))

    m_e141 = np.geomspace(0.008, 0.017, 60)
    y_e141_lo = 1.6e-5 * (m_e141 / 0.008) ** 1.2
    y_e141_hi = 1.3e-4 * (0.017 / m_e141) ** 0.5

    m_e137 = np.geomspace(0.008, 0.095, 90)
    t_e137 = np.log10(m_e137 / 0.008) / np.log10(0.095 / 0.008)
    y_e137_lo = 2.5e-7 * np.ones_like(m_e137)
    y_e137_hi = 2.8e-6 * np.exp(-1.7 * t_e137**2.4)

    existing = [
        {
            "x": m_na64,
            "y_low": y_na64,
            "y_high": np.full_like(m_na64, 4.0e-3),
            "label": "NA64",
            "text_pos": (0.014, 1.05e-3),
        },
        {
            "x": m_babar,
            "y_low": y_babar,
            "y_high": np.full_like(m_babar, 4.0e-3),
            "label": "BaBar",
            "text_pos": (0.095, 9.2e-4),
        },
        {
            "x": m_kloe,
            "y_low": y_kloe,
            "y_high": np.full_like(m_kloe, 4.0e-3),
            "label": "KLOE",
            "text_pos": (0.38, 2.0e-3),
        },
        {
            "x": m_e141,
            "y_low": y_e141_lo,
            "y_high": y_e141_hi,
            "label": "E141",
            "text_pos": (0.0102, 5.2e-5),
        },
        {
            "x": m_e137,
            "y_low": y_e137_lo,
            "y_high": y_e137_hi,
            "label": "E137",
            "text_pos": (0.022, 8.0e-7),
        },
    ]

    # FASER expected, ±1σ expected band, and observed 90% CL contours
    x_exp, y_exp = _beam_dump_lobe(0.014, 0.140, 2.3e-5, 0.60)
    x_obs, y_obs = _beam_dump_lobe(0.0145, 0.132, 2.5e-5, 0.57)
    x_s1, y_s1 = _beam_dump_lobe(0.013, 0.158, 2.2e-5, 0.68)

    excl = fms.plot_exclusion(
        x_obs,
        y_obs,
        expected=(x_exp, y_exp),
        one_sigma=(x_s1, y_s1),
        existing=existing,
        observed_label="FASER Observed (90% CL)",
        expected_label=r"FASER Expected ($\pm 1\sigma_{\mathrm{exp}}$)",
        existing_label="Existing Limits",
        hatch="//",
        fill_alpha=0.0,
        linewidth=2.2,
        ax=ax,
    )

    ax.set_xlim(8.0e-3, 0.80)
    ax.set_ylim(2.5e-7, 4.0e-3)

    fms.draw_faser_logo(
        ax=ax,
        width=0.25,
        loc="lower right",
        com=13.6,
        lumi=186,
        desc=r"Dark Photon ($A' \to e^+e^-$)",
        layout="stacked",
        color="black",
    )

    ax.legend(
        handles=[
            excl["existing"][0],
            (excl["one_sigma"], excl["expected"]),
            excl["observed"],
        ],
        labels=[
            "Existing Limits",
            r"FASER Expected ($\pm 1\sigma_{\mathrm{exp}}$)",
            "FASER Observed (90% CL)",
        ],
        loc="upper right",
        bbox_to_anchor=(0.99, 0.77),
    )

    fms.set_xlabel(r"Dark Photon Mass $m_{A'}$ [GeV]", ax=ax)
    fms.set_ylabel(r"Kinetic Mixing $\varepsilon$", ax=ax)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "02_dark_photon_exclusion.png"
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
