from __future__ import annotations

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

import faser_mpl_style as fms


class TestPublicationVisualRegression:
    def test_stacked_spectrum_with_ratio_png_and_pdf(self, tmp_path: Path) -> None:
        fms.use_faser_style("faser")
        bins = np.linspace(100.0, 1100.0, 11)
        mc_numu = np.array([120, 210, 260, 220, 175, 130, 95, 65, 42, 28], dtype=float)
        mc_nue = np.array([18, 35, 48, 42, 32, 24, 16, 11, 7, 4], dtype=float)
        mc_err_numu = 0.12 * mc_numu
        mc_err_nue = 0.15 * mc_nue
        data = np.array([142, 238, 315, 255, 212, 149, 108, 79, 46, 33], dtype=float)

        fig, ax, rax = fms.ratio_axes()
        total, total_err = fms.plot_mc_stack(
            bins,
            [mc_numu, mc_nue],
            labels=[r"$\nu_\mu + \bar{\nu}_\mu$", r"$\nu_e + \bar{\nu}_e$"],
            yerr=[mc_err_numu, mc_err_nue],
            ax=ax,
        )
        fms.plot_data(bins, data, yerr="poisson", label="Data", ax=ax)
        fms.plot_ratio(
            bins,
            data,
            total,
            num_err=fms.poisson_errors(data),
            den_err=total_err,
            ax=rax,
        )
        fms.draw_faser_label(
            ax=ax,
            experiment="FASERν",
            status="prelim",
            com=13.6,
            lumi=65.6,
            desc="Calorimeter region",
            pad_y=0.30,
        )
        ax.legend(loc="upper right")
        fms.set_xlabel(r"$E_{\mathrm{cal}}\ [\mathrm{GeV}]$", ax=ax)
        fms.set_ylabel("Events / 100 GeV", ax=ax)

        png_out = tmp_path / "spectrum_ratio.png"
        pdf_out = tmp_path / "spectrum_ratio.pdf"
        fig.savefig(png_out)
        fig.savefig(pdf_out)

        assert png_out.stat().st_size > 10_000
        assert pdf_out.stat().st_size > 5_000
        img = mpimg.imread(png_out)
        assert img.shape[0] > 500 and img.shape[1] > 500

    def test_2d_exclusion_contour_with_logo(self, tmp_path: Path) -> None:
        fms.use_faser_style("faser")
        x = np.geomspace(1.5e-2, 1.2e-1, 40)
        t = (np.log10(x) - np.log10(1.5e-2)) / (np.log10(1.2e-1) - np.log10(1.5e-2))
        arch = np.sin(np.pi * t) ** 0.7
        y_low = 3e-5 * 10 ** (-0.7 * arch)
        y_high = 3e-5 * 10 ** (0.8 * arch)

        existing = [
            {
                "x": np.geomspace(5e-3, 5e-1, 20),
                "y_low": np.full(20, 4e-4),
                "y_high": np.full(20, 5e-3),
                "label": "NA64 / BaBar",
                "text_pos": (4e-2, 1.5e-3),
            }
        ]

        fig, ax = plt.subplots()
        fms.plot_exclusion(
            x,
            y_low,
            y_high,
            expected=(x, y_low * 1.08, y_high * 0.92),
            one_sigma=(x, y_low * 0.85, y_high * 1.18),
            existing=existing,
            hatch="//",
            ax=ax,
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(5e-3, 5e-1)
        ax.set_ylim(1e-6, 5e-3)
        fms.draw_faser_logo(
            ax=ax,
            loc="lower left",
            status="Preliminary",
            com=13.6,
            lumi=186,
        )
        ax.legend(loc="lower right")
        fms.set_xlabel(r"$m_{A'}\ [\mathrm{GeV}]$", ax=ax)
        fms.set_ylabel(r"$\varepsilon$", ax=ax)

        png_out = tmp_path / "exclusion.png"
        pdf_out = tmp_path / "exclusion.pdf"
        fig.savefig(png_out)
        fig.savefig(pdf_out)

        assert png_out.stat().st_size > 10_000
        assert pdf_out.stat().st_size > 5_000

    def test_2d_heatmap_with_outside_logo(self, tmp_path: Path) -> None:
        fms.use_faser_style("faser")
        xbins = np.linspace(-100.0, 100.0, 21)
        ybins = np.linspace(-100.0, 100.0, 21)
        xc = 0.5 * (xbins[:-1] + xbins[1:])
        yc = 0.5 * (ybins[:-1] + ybins[1:])
        xx, yy = np.meshgrid(xc, yc)
        eff = np.exp(-(xx**2 + yy**2) / (2 * 65.0**2))

        fig, ax = plt.subplots()
        fms.plot_2d(xbins, ybins, eff, cmap="faser_bird", zlabel="Efficiency", ax=ax)
        fms.draw_faser_logo(ax=ax, loc="outside", lumi=65.6)
        fms.set_xlabel(r"$x\ [\mathrm{mm}]$", ax=ax)
        fms.set_ylabel(r"$y\ [\mathrm{mm}]$", ax=ax)

        png_out = tmp_path / "heatmap_bird.png"
        pdf_out = tmp_path / "heatmap_bird.pdf"
        fig.savefig(png_out)
        fig.savefig(pdf_out)

        assert png_out.stat().st_size > 10_000
        assert pdf_out.stat().st_size > 5_000

    def test_brazil_limit_and_ratio(self, tmp_path: Path) -> None:
        fms.use_faser_style("faser")
        masses = np.linspace(100.0, 500.0, 9)
        exp = 10.0 * np.exp(-masses / 300.0)
        obs = exp * np.array([0.92, 1.05, 1.12, 0.96, 0.88, 1.04, 1.15, 0.98, 1.01])

        fig, ax, rax = fms.ratio_axes()
        fms.plot_limit(
            masses,
            exp,
            observed=obs,
            one_sigma=(exp * 0.72, exp * 1.38),
            two_sigma=(exp * 0.52, exp * 1.85),
            ax=ax,
        )
        fms.plot_ratio(
            masses,
            obs,
            exp,
            ylabel=r"Obs. / Exp.",
            ylim=(0.5, 1.5),
            ax=rax,
        )
        fms.draw_faser_label(ax=ax, com=13.6, lumi=186, pad_y=0.3)
        ax.legend(loc="upper right")
        fms.set_xlabel(r"$m_X\ [\mathrm{GeV}]$", ax=ax)
        fms.set_ylabel(r"95% CL Upper Limit on $\sigma\ [\mathrm{fb}]$", ax=ax)

        png_out = tmp_path / "brazil_limit.png"
        fig.savefig(png_out)
        assert png_out.stat().st_size > 10_000

    def test_transparent_logo_over_colored_background_has_no_white_box(
        self, tmp_path: Path
    ) -> None:
        fms.use_faser_style("faser")

        # 1) Black logo over vivid coral-red background patch
        fig, ax = plt.subplots(figsize=(6.0, 4.5), dpi=150)
        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.0)
        ax.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, facecolor="#E04040", edgecolor="none", zorder=1))
        ax.set_xticks([])
        ax.set_yticks([])
        fms.draw_faser_logo(ax=ax, loc="upper left", width=0.45, color="black", zorder=10)

        png_dark = tmp_path / "logo_over_red.png"
        fig.savefig(png_dark, bbox_inches=None)
        fig.canvas.draw()
        # Sample strictly inside the axes bounding box in rendered image pixels
        img = mpimg.imread(png_dark)
        h, w = img.shape[:2]
        pos = ax.get_position()
        y0 = int((1.0 - pos.y1) * h) + 6
        y1 = int((1.0 - pos.y0) * h) - 6
        x0 = int(pos.x0 * w) + 6
        x1 = int(pos.x1 * w) - 6
        interior = img[y0:y1, x0:x1, :3]

        # Must have ZERO white pixels inside the red axes (no opaque white box behind logo!)
        white_mask = (interior[..., 0] > 0.92) & (interior[..., 1] > 0.92) & (interior[..., 2] > 0.92)
        assert int(np.count_nonzero(white_mask)) == 0

        # Must contain both dark logo ink and intact coral-red background in the upper-left logo zone
        logo_zone = interior[: interior.shape[0] // 2, : int(interior.shape[1] * 0.6)]
        dark_ink = (logo_zone[..., 0] < 0.15) & (logo_zone[..., 1] < 0.15) & (logo_zone[..., 2] < 0.15)
        red_bg = (logo_zone[..., 0] > 0.75) & (logo_zone[..., 1] < 0.35) & (logo_zone[..., 2] < 0.35)
        assert int(np.count_nonzero(dark_ink)) > 100
        assert int(np.count_nonzero(red_bg)) > 500
        plt.close(fig)

        # 2) White-tinted logo over deep navy background patch
        fig2, ax2 = plt.subplots(figsize=(6.0, 4.5), dpi=150)
        ax2.set_xlim(0.0, 1.0)
        ax2.set_ylim(0.0, 1.0)
        ax2.add_patch(Rectangle((0.0, 0.0), 1.0, 1.0, facecolor="#0B2545", edgecolor="none", zorder=1))
        ax2.set_xticks([])
        ax2.set_yticks([])
        fms.draw_faser_logo(ax=ax2, loc="upper left", width=0.45, color="white", zorder=10)

        png_white = tmp_path / "logo_white_over_navy.png"
        fig2.savefig(png_white, bbox_inches=None)
        img2 = mpimg.imread(png_white)
        h2, w2 = img2.shape[:2]
        pos2 = ax2.get_position()
        int2 = img2[
            int((1.0 - pos2.y1) * h2) + 6 : int((1.0 - pos2.y0) * h2) - 6,
            int(pos2.x0 * w2) + 6 : int(pos2.x1 * w2) - 6,
            :3,
        ]
        zone2 = int2[: int2.shape[0] // 2, : int(int2.shape[1] * 0.6)]
        white_ink = (zone2[..., 0] > 0.90) & (zone2[..., 1] > 0.90) & (zone2[..., 2] > 0.90)
        navy_bg = (zone2[..., 0] < 0.15) & (zone2[..., 1] < 0.25) & (zone2[..., 2] > 0.20)
        assert int(np.count_nonzero(white_ink)) > 100
        assert int(np.count_nonzero(navy_bg)) > 500
