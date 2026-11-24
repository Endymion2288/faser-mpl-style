from __future__ import annotations

import builtins
import io
import sys
import warnings

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import PolyCollection, QuadMesh
from matplotlib.colorbar import Colorbar
from matplotlib.container import ErrorbarContainer
from matplotlib.patches import StepPatch
from matplotlib.ticker import MaxNLocator

import faser_mpl_style as fms

# Exact 1-sigma (68.268949%) Garwood chi-squared Poisson errors: (lower, upper)
# Computed from 0.5 * chi2.ppf(alpha/2, 2*N) and 0.5 * chi2.ppf(1 - alpha/2, 2*(N+1))
# with alpha = 1 - erf(1/sqrt(2)) = 0.31731050786291415.
GARWOOD_REFERENCE: dict[int, tuple[float, float]] = {
    0: (0.0, 1.8410216450098775),
    1: (0.8272462209765501, 2.299526561375637),
    5: (2.159712883698826, 3.382524143929018),
    10: (3.1086261797268454, 4.266949235648499),
    50: (7.046848244162889, 8.117347471770492),
    100: (9.983017014796199, 11.032993416863532),
    1000: (31.617421599941626, 32.63345728219235),
}


class TestRatioAxes:
    def test_single_ratio_axes_structure_and_linking(self) -> None:
        fms.use_faser_style("faser")
        fig, main_ax, ratio_ax = fms.ratio_axes()

        assert main_ax.get_shared_x_axes().joined(main_ax, ratio_ax)
        assert hasattr(main_ax, "_faser_linked_axes")
        assert ratio_ax in main_ax._faser_linked_axes

        fig.canvas.draw()
        assert not any(lbl.get_visible() for lbl in main_ax.get_xticklabels())
        assert any(lbl.get_visible() for lbl in ratio_ax.get_xticklabels())

    def test_extra_axes_returns_list(self) -> None:
        fms.use_faser_style("faser")
        fig, main_ax, ratio_list = fms.ratio_axes(extra_axes=1)

        assert isinstance(ratio_list, list)
        assert len(ratio_list) == 2
        assert main_ax.get_shared_x_axes().joined(main_ax, ratio_list[0])
        assert main_ax.get_shared_x_axes().joined(main_ax, ratio_list[1])

        fig.canvas.draw()
        assert not any(lbl.get_visible() for lbl in main_ax.get_xticklabels())
        assert not any(lbl.get_visible() for lbl in ratio_list[0].get_xticklabels())
        assert any(lbl.get_visible() for lbl in ratio_list[1].get_xticklabels())

    def test_hspace_zero_prunes_upper_ratio_tick(self) -> None:
        fms.use_faser_style("faser")
        fig, _main_ax, ratio_ax = fms.ratio_axes(hspace=0.0)

        locator = ratio_ax.yaxis.get_major_locator()
        assert isinstance(locator, MaxNLocator)
        assert locator._prune == "upper"
        fig.savefig(io.BytesIO(), format="png")


class TestPoissonErrors:
    def test_garwood_accuracy_reference_counts(self) -> None:
        counts = np.array(list(GARWOOD_REFERENCE.keys()), dtype=float)
        errs = fms.poisson_errors(counts, method="garwood")
        assert errs.shape == (2, len(counts))

        for idx, n in enumerate(GARWOOD_REFERENCE):
            exp_lo, exp_hi = GARWOOD_REFERENCE[n]
            assert errs[0, idx] == pytest.approx(exp_lo, rel=2e-4, abs=1e-6)
            assert errs[1, idx] == pytest.approx(exp_hi, rel=2e-4, abs=1e-6)

    def test_garwood_without_scipy_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        real_import = builtins.__import__

        def blocked_scipy_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "scipy" or name.startswith("scipy."):
                raise ImportError("scipy blocked for test")
            return real_import(name, *args, **kwargs)

        monkeypatch.setitem(sys.modules, "scipy", None)
        monkeypatch.setitem(sys.modules, "scipy.stats", None)
        monkeypatch.setattr(builtins, "__import__", blocked_scipy_import)

        counts = np.array(list(GARWOOD_REFERENCE.keys()), dtype=float)
        errs = fms.poisson_errors(counts, method="garwood")
        assert errs.shape == (2, len(counts))

        for idx, n in enumerate(GARWOOD_REFERENCE):
            exp_lo, exp_hi = GARWOOD_REFERENCE[n]
            assert errs[0, idx] == pytest.approx(exp_lo, rel=5e-4, abs=1e-6)
            assert errs[1, idx] == pytest.approx(exp_hi, rel=5e-4, abs=1e-6)

    def test_sqrt_method(self) -> None:
        counts = np.array([0, 1, 4, 25, 100], dtype=float)
        errs = fms.poisson_errors(counts, method="sqrt")
        assert errs.shape == (2, 5)
        expected = np.sqrt(counts)
        assert np.allclose(errs[0], expected)
        assert np.allclose(errs[1], expected)

    def test_negative_counts_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="negative"):
            fms.poisson_errors([-1, 5, 10])


class TestPlot1DAndData:
    def test_plot_1d_fill_band_hatch_and_autolim(self) -> None:
        fms.use_faser_style("faser")
        bins = np.linspace(0.0, 10.0, 6)
        vals = np.array([10.0, 25.0, 40.0, 20.0, 5.0])
        yerr = np.array([2.0, 3.0, 4.0, 2.5, 1.5])

        fig, ax = plt.subplots()
        stairs = fms.plot_1d(
            bins,
            vals,
            yerr=yerr,
            label="MC",
            fill=True,
            band=True,
            band_hatch="///",
            autolim=True,
            ax=ax,
        )
        assert isinstance(stairs, StepPatch)
        assert ax.get_xlim() == pytest.approx((0.0, 10.0))
        assert len(ax.collections) >= 1

        # Asymmetric yerr + autolim=False
        _fig2, ax2 = plt.subplots()
        ax2.set_xlim(-5.0, 20.0)
        fms.plot_1d(
            bins,
            vals,
            yerr=np.vstack([yerr * 0.5, yerr]),
            band=True,
            autolim=False,
            ax=ax2,
        )
        assert ax2.get_xlim() == pytest.approx((-5.0, 20.0))
        fig.savefig(io.BytesIO(), format="png")

    def test_plot_data_edges_centers_yerr_xerr_show_zero(self) -> None:
        fms.use_faser_style("faser")
        bins = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        centers = 0.5 * (bins[:-1] + bins[1:])
        counts = np.array([0.0, 12.0, 25.0, 0.0])

        # Bin edges + poisson + xerr=True + show_zero=False
        fig, ax = plt.subplots()
        eb = fms.plot_data(bins, counts, yerr="poisson", xerr=True, show_zero=False, ax=ax)
        assert isinstance(eb, ErrorbarContainer)
        x_plotted, y_plotted = eb.lines[0].get_data()
        assert len(x_plotted) == 2
        assert np.allclose(x_plotted, [1.5, 2.5])
        assert np.allclose(y_plotted, [12.0, 25.0])
        fig.savefig(io.BytesIO(), format="png")

        # Bin centers + sqrt + show_zero=True
        _fig2, ax2 = plt.subplots()
        eb2 = fms.plot_data(centers, counts, yerr="sqrt", show_zero=True, ax=ax2)
        assert len(eb2.lines[0].get_xdata()) == 4

        # Explicit array yerr
        _fig3, ax3 = plt.subplots()
        eb3 = fms.plot_data(
            bins,
            np.array([5.0, 10.0, 15.0, 20.0]),
            yerr=np.array([1.0, 2.0, 2.5, 3.0]),
            ax=ax3,
        )
        assert isinstance(eb3, ErrorbarContainer)


class TestPlotMCStackAndBand:
    def test_plot_mc_stack_quadrature_and_styles(self) -> None:
        fms.use_faser_style("faser")
        bins = np.linspace(0.0, 500.0, 6)
        h1 = np.array([10.0, 20.0, 30.0, 20.0, 10.0])
        h2 = np.array([5.0, 10.0, 15.0, 10.0, 5.0])
        e1 = np.array([3.0, 4.0, 5.0, 4.0, 3.0])
        e2 = np.array([4.0, 3.0, 12.0, 3.0, 4.0])

        fig, ax = plt.subplots()
        total, total_err = fms.plot_mc_stack(
            bins,
            [h1, h2],
            labels=[r"$\nu_\mu$", r"$\nu_e$"],
            yerr=[e1, e2],
            err_style="hatch",
            ax=ax,
        )
        assert np.allclose(total, h1 + h2)
        assert total_err is not None
        assert np.allclose(total_err, np.sqrt(e1**2 + e2**2))
        fig.savefig(io.BytesIO(), format="png")

        # Explicit total_err with fill style
        fig2, ax2 = plt.subplots()
        explicit_err = np.full(5, 2.5)
        total2, total_err2 = fms.plot_mc_stack(
            bins,
            [h1, h2],
            labels=["A", "B"],
            total_err=explicit_err,
            err_style="fill",
            ax=ax2,
        )
        assert np.allclose(total2, h1 + h2)
        assert total_err2 is not None
        assert np.allclose(total_err2, explicit_err)
        fig2.savefig(io.BytesIO(), format="png")

        # No errors provided
        _fig3, ax3 = plt.subplots()
        total3, total_err3 = fms.plot_mc_stack(bins, [h1, h2], labels=["A", "B"], ax=ax3)
        assert np.allclose(total3, h1 + h2)
        assert total_err3 is None

    def test_plot_band_continuous_and_binned(self) -> None:
        fms.use_faser_style("faser")

        # Continuous
        fig, ax = plt.subplots()
        x = np.linspace(0.0, 10.0, 20)
        poly_c = fms.plot_band(x, np.sin(x) - 0.2, np.sin(x) + 0.2, color="faser:blue", ax=ax)
        assert isinstance(poly_c, PolyCollection)

        # Binned edges (len(x) == len(low) + 1) with transparent hatch
        bins = np.array([0.0, 2.0, 5.0, 10.0])
        low = np.array([0.8, 0.9, 0.85])
        high = np.array([1.2, 1.1, 1.15])
        poly_b = fms.plot_band(bins, low, high, hatch="////", ax=ax)
        assert isinstance(poly_b, PolyCollection)
        assert poly_b.get_hatch() == "////"
        # Check span covers full bin edges [0, 10]
        verts = poly_b.get_paths()[0].vertices
        assert verts[:, 0].min() == pytest.approx(0.0)
        assert verts[:, 0].max() == pytest.approx(10.0)
        fig.savefig(io.BytesIO(), format="png")


class TestPlotRatio:
    @pytest.mark.parametrize("mode", ("ratio", "diff", "pull"))
    def test_plot_ratio_modes_zero_denom_and_offscale_arrows(self, mode: str) -> None:
        fms.use_faser_style("faser")
        bins = np.linspace(0.0, 6.0, 7)
        num = np.array([12.0, 5.0, 100.0, 2.0, 18.0, 10.0])
        den = np.array([10.0, 0.0, 20.0, 20.0, 20.0, 0.0])  # contains zeros + offscale points
        num_err = np.sqrt(num)
        den_err = np.array([1.5, 0.0, 2.0, 2.0, 2.0, 0.0])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fig, ax = plt.subplots()
            eb = fms.plot_ratio(
                bins,
                num,
                den,
                num_err=num_err,
                den_err=den_err,
                mode=mode,  # type: ignore[arg-type]
                offscale_arrows=True,
                xerr=True,
                ax=ax,
            )
            fig.savefig(io.BytesIO(), format="png")

        assert isinstance(eb, ErrorbarContainer)
        bad_warnings = [
            w for w in caught if issubclass(w.category, (RuntimeWarning, UserWarning))
        ]
        assert bad_warnings == [], [str(w.message) for w in bad_warnings]

        # Ensure offscale arrows were drawn in ratio mode (100/20 = 5.0 > 1.5, 2/20 = 0.1 < 0.5)
        if mode == "ratio":
            assert ax.get_ylim() == pytest.approx((0.5, 1.5))
            # Both an upper and lower offscale indicator should appear among lines/collections
            n_artists = len(ax.lines) + len(ax.collections)
            assert n_artists >= 3


class TestPlotLimitExclusionAnd2D:
    @pytest.mark.parametrize("band_palette", ("faser", "atlas"))
    def test_plot_limit_palettes(self, band_palette: str) -> None:
        fms.use_faser_style("faser")
        x = np.linspace(1.0, 10.0, 8)
        exp = np.full_like(x, 1.0)
        obs = np.linspace(0.9, 1.2, 8)
        one_s = (exp * 0.7, exp * 1.4)
        two_s = (exp * 0.5, exp * 1.9)

        fig, ax = plt.subplots()
        artists = fms.plot_limit(
            x,
            exp,
            observed=obs,
            one_sigma=one_s,
            two_sigma=two_s,
            band_palette=band_palette,  # type: ignore[arg-type]
            ax=ax,
        )
        assert set(artists.keys()) == {"two_sigma", "one_sigma", "expected", "observed"}

        expected_1s_hex = (
            mcolors.to_hex("faser:onesigma")
            if band_palette == "faser"
            else mcolors.to_hex("faser:atlas-onesigma")
        )
        fc_1s = artists["one_sigma"].get_facecolor()[0]
        assert mcolors.to_hex(fc_1s[:3]).lower() == expected_1s_hex.lower()
        fig.savefig(io.BytesIO(), format="png")

    def test_plot_exclusion_envelope_and_polygon(self) -> None:
        fms.use_faser_style("faser")

        # Envelope mode with expected, 1sigma, existing regions, and hatching
        x = np.geomspace(1e-2, 1e-1, 20)
        y_lo = 1e-5 * np.ones_like(x)
        y_hi = 1e-4 * np.ones_like(x)
        existing = [
            {
                "x": np.geomspace(5e-3, 2e-1, 10),
                "y_low": np.full(10, 5e-4),
                "y_high": np.full(10, 1e-2),
                "label": "BaBar",
                "text_pos": (2e-2, 2e-3),
            },
            {
                "x": [5e-3, 1.5e-2, 1.5e-2, 5e-3],
                "y": [1e-6, 1e-6, 5e-5, 5e-5],
                "label": "E141",
                "text_pos": (8e-3, 5e-6),
                "rotation": 15,
            },
        ]

        fig, ax = plt.subplots()
        res_env = fms.plot_exclusion(
            x,
            y_lo,
            y_hi,
            expected=(x, y_lo * 1.1, y_hi * 0.9),
            one_sigma=(x, y_lo * 0.8, y_hi * 1.2),
            existing=existing,
            hatch="//",
            fill_alpha=0.1,
            ax=ax,
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        assert isinstance(res_env, dict)
        assert len(res_env) >= 3
        fig.savefig(io.BytesIO(), format="png")

        # Polygon mode (y_high=None)
        theta = np.linspace(0, 2 * np.pi, 30)
        xp = 0.05 + 0.02 * np.cos(theta)
        yp = 1e-4 * 10 ** (0.3 * np.sin(theta))
        fig2, ax2 = plt.subplots()
        res_poly = fms.plot_exclusion(
            xp,
            yp,
            expected=(xp, yp * 1.1),
            one_sigma=(xp, yp * 1.3),
            ax=ax2,
        )
        assert isinstance(res_poly, dict)
        assert len(res_poly) >= 2
        fig2.savefig(io.BytesIO(), format="png")

    @pytest.mark.parametrize("cmap", ("viridis", "faser_bird", "faser_blues"))
    def test_plot_2d_linear_logz_and_no_colorbar(self, cmap: str) -> None:
        fms.use_faser_style("faser")
        xbins = np.linspace(0.0, 10.0, 6)
        ybins = np.linspace(-5.0, 5.0, 5)
        vals = np.array(
            [
                [0.0, 1.0, 5.0, 12.0, 0.0],
                [2.0, 15.0, 40.0, 8.0, 1.0],
                [0.0, 10.0, 30.0, 5.0, 0.0],
                [1.0, 3.0, 6.0, 2.0, 0.0],
            ]
        )

        # Log z with zeros + colorbar + zlabel
        fig, ax = plt.subplots()
        mesh, cbar = fms.plot_2d(
            xbins,
            ybins,
            vals,
            cmap=cmap,
            logz=True,
            zlabel="Events / bin",
            ax=ax,
        )
        assert isinstance(mesh, QuadMesh)
        assert isinstance(cbar, Colorbar)
        assert isinstance(mesh.norm, mcolors.LogNorm)
        assert cbar.ax.get_ylabel() == "Events / bin"
        fig.savefig(io.BytesIO(), format="png")

        # Linear without colorbar
        fig2, ax2 = plt.subplots()
        mesh2, cbar2 = fms.plot_2d(xbins, ybins, vals, cmap=cmap, colorbar=False, ax=ax2)
        assert isinstance(mesh2, QuadMesh)
        assert cbar2 is None
        fig2.savefig(io.BytesIO(), format="png")
