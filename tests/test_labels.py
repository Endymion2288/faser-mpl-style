from __future__ import annotations

import importlib.resources as importlib_resources
import io

import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.artist import Artist
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.text import Text

import faser_mpl_style as fms


def _collect_texts(artists: list[Artist]) -> str:
    """Extract all text strings from Text artists or OffsetBox TextAreas."""
    parts: list[str] = []
    for artist in artists:
        if isinstance(artist, Text):
            parts.append(artist.get_text())
        elif isinstance(artist, AnnotationBbox):
            stack = [artist.offsetbox]
            while stack:
                box = stack.pop()
                if hasattr(box, "_text") and isinstance(box._text, Text):
                    parts.append(box._text.get_text())
                if hasattr(box, "get_children"):
                    stack.extend(box.get_children())
    return "\n".join(parts)


def _find_offset_images(artists: list[Artist]) -> list[OffsetImage]:
    """Recursively collect OffsetImage children inside returned artists."""
    found: list[OffsetImage] = []
    for artist in artists:
        if isinstance(artist, OffsetImage):
            found.append(artist)
        elif isinstance(artist, AnnotationBbox):
            stack = [artist.offsetbox]
            while stack:
                box = stack.pop()
                if isinstance(box, OffsetImage):
                    found.append(box)
                if hasattr(box, "get_children"):
                    stack.extend(box.get_children())
    return found


class TestStatusAliases:
    @pytest.mark.parametrize(
        ("alias", "expected"),
        [
            ("", ""),
            ("final", ""),
            ("published", ""),
            ("prelim", "Preliminary"),
            ("preliminary", "Preliminary"),
            ("int", "Internal"),
            ("internal", "Internal"),
            ("sim", "Simulation"),
            ("simulation", "Simulation"),
            ("sim_prelim", "Simulation Preliminary"),
            ("sim-prelim", "Simulation Preliminary"),
            ("simulation preliminary", "Simulation Preliminary"),
            ("sim_int", "Simulation Internal"),
            ("sim-int", "Simulation Internal"),
            ("simulation internal", "Simulation Internal"),
            ("wip", "Work in Progress"),
            ("work in progress", "Work in Progress"),
            ("testbeam", "Testbeam"),
            ("test beam", "Test Beam"),
        ],
    )
    def test_status_aliases_mapping(self, alias: str, expected: str) -> None:
        assert fms.STATUS_ALIASES[alias] == expected


class TestDrawFaserLabel:
    @pytest.mark.parametrize("experiment", ("FASER", "FASERv", "FASERν", "FASER2"))
    def test_experiments_render_cleanly(self, experiment: str) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        artists = fms.draw_faser_label(ax=ax, experiment=experiment, status="prelim")
        assert len(artists) >= 1
        assert all(isinstance(a, Artist) for a in artists)

        combined = _collect_texts(artists)
        assert "FASER" in combined
        assert "Preliminary" in combined
        if experiment in {"FASERv", "FASERν"}:
            assert ("\\nu" in combined) or ("ν" in combined)
        if experiment == "FASER2":
            assert "2" in combined

        fig.savefig(io.BytesIO(), format="png")

    def test_simulation_composition(self) -> None:
        fms.use_faser_style("faser")

        _fig1, ax1 = plt.subplots()
        a1 = fms.draw_faser_label(ax=ax1, simulation=True)
        t1 = _collect_texts(a1)
        assert "Simulation" in t1

        _fig2, ax2 = plt.subplots()
        a2 = fms.draw_faser_label(ax=ax2, status="prelim", simulation=True)
        t2 = _collect_texts(a2)
        assert "Simulation Preliminary" in t2

        # Must not duplicate Simulation when already present in status
        _fig3, ax3 = plt.subplots()
        a3 = fms.draw_faser_label(ax=ax3, status="sim_prelim", simulation=True)
        t3 = _collect_texts(a3)
        assert "Simulation Preliminary" in t3
        assert "Simulation Simulation" not in t3

        # Unrecognized status preserved verbatim
        _fig4, ax4 = plt.subplots()
        a4 = fms.draw_faser_label(ax=ax4, status="Custom Note")
        assert "Custom Note" in _collect_texts(a4)

    @pytest.mark.parametrize(
        ("lumi_prefix", "expected_substr"),
        [
            ("L", "L = 65.6"),
            ("calL", r"\mathcal{L} = 65.6"),
            ("", "65.6"),
        ],
    )
    def test_com_lumi_prefixes_and_desc(self, lumi_prefix: str, expected_substr: str) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        artists = fms.draw_faser_label(
            ax=ax,
            status="final",
            com=13.6,
            lumi=65.6,
            lumi_prefix=lumi_prefix,
            desc=["Calorimeter selection", r"$E_{\mathrm{cal}} > 100\ \mathrm{GeV}$"],
        )
        text = _collect_texts(artists)
        assert "13.6" in text
        assert "TeV" in text
        assert expected_substr in text
        if lumi_prefix == "":
            assert "L =" not in text
            assert r"\mathcal{L}" not in text
        assert "Calorimeter selection" in text
        assert "100" in text

        fig.savefig(io.BytesIO(), format="png")

    def test_desc_single_string_and_verbatim_lumi(self) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        artists = fms.draw_faser_label(
            ax=ax,
            com="13.6 TeV",
            lumi=r"$35.4\ \mathrm{fb}^{-1}$",
            desc="Single description line",
        )
        text = _collect_texts(artists)
        assert "13.6 TeV" in text
        assert "TeV TeV" not in text
        assert "35.4" in text
        assert "Single description line" in text
        fig.savefig(io.BytesIO(), format="png")

    @pytest.mark.parametrize(
        "loc", ("upper left", "upper right", "lower left", "lower right", "outside")
    )
    def test_all_five_locations(self, loc: str) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        artists = fms.draw_faser_label(
            ax=ax,
            status="prelim",
            com=13.6,
            lumi=186,
            desc="Test desc",
            loc=loc,  # type: ignore[arg-type]
        )
        assert len(artists) >= 1
        fig.savefig(io.BytesIO(), format="png")

    def test_style_logo_delegates_to_draw_faser_logo(self) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        artists = fms.draw_faser_label(
            ax=ax,
            style="logo",
            status="Preliminary",
            com=13.6,
            lumi=186,
            logo_width=0.25,
            logo_color="faser:blue",
        )
        imgs = _find_offset_images(artists)
        assert len(imgs) == 1
        fig.savefig(io.BytesIO(), format="png")

    def test_pad_y_linear_and_log_headroom(self) -> None:
        fms.use_faser_style("faser")

        # Linear scale
        _fig1, ax1 = plt.subplots()
        ax1.plot([0, 1], [0, 100])
        ax1.set_ylim(0, 100)
        fms.draw_faser_label(ax=ax1, status="prelim", pad_y=0.30)
        lo1, hi1 = ax1.get_ylim()
        assert lo1 == pytest.approx(0.0)
        assert hi1 == pytest.approx(130.0)

        # Log scale
        _fig2, ax2 = plt.subplots()
        ax2.plot([0, 1], [1, 1e4])
        ax2.set_yscale("log")
        ax2.set_ylim(1.0, 1e4)
        fms.draw_faser_label(ax=ax2, status="prelim", pad_y=0.25)
        lo2, hi2 = ax2.get_ylim()
        assert lo2 == pytest.approx(1.0)
        assert hi2 == pytest.approx(1e5)


class TestDrawFaserLogo:
    def test_bundled_logo_asset_is_transparent_rgba(self) -> None:
        asset = importlib_resources.files("faser_mpl_style.assets").joinpath("faser_logo.png")
        with importlib_resources.as_file(asset) as logo_path:
            img = mpimg.imread(logo_path)

        assert img.ndim == 3
        assert img.shape[2] == 4
        alpha_u8 = np.rint(img[..., 3] * 255).astype(np.uint8) if img.dtype.kind == "f" else img[..., 3]

        # All four corners must be completely transparent
        assert alpha_u8[0, 0] == 0
        assert alpha_u8[0, -1] == 0
        assert alpha_u8[-1, 0] == 0
        assert alpha_u8[-1, -1] == 0
        # Solid ink interior must reach full opacity 255
        assert int(alpha_u8.max()) == 255
        assert int(np.count_nonzero(alpha_u8 == 255)) > 1000

    @pytest.mark.parametrize("layout", ("stacked", "inline"))
    def test_logo_layouts_render(self, layout: str) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        artists = fms.draw_faser_logo(
            ax=ax,
            layout=layout,  # type: ignore[arg-type]
            status="Preliminary",
            com=13.6,
            lumi=186,
            desc="Dark photon search",
        )
        assert len(_find_offset_images(artists)) == 1
        fig.savefig(io.BytesIO(), format="png")

    def test_logo_outside_location(self) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        artists = fms.draw_faser_logo(
            ax=ax,
            loc="outside",
            status="Preliminary",
            com=13.6,
            lumi=65.6,
        )
        assert len(_find_offset_images(artists)) == 1
        text = _collect_texts(artists)
        assert "65.6" in text
        fig.savefig(io.BytesIO(), format="png")

    @pytest.mark.parametrize("tint", ("white", "faser:blue"))
    def test_logo_runtime_color_tinting(self, tint: str) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        artists = fms.draw_faser_logo(ax=ax, color=tint)
        imgs = _find_offset_images(artists)
        assert len(imgs) == 1

        arr = np.asarray(imgs[0].get_data())
        assert arr.ndim == 3 and arr.shape[2] == 4
        # Corners remain transparent
        assert arr[0, 0, 3] == 0

        opaque = arr[..., 3] > 250
        assert np.any(opaque)
        expected_rgb = np.rint(np.array(mcolors.to_rgb(tint)) * 255).astype(np.uint8)
        actual_rgb = (
            np.rint(arr[opaque, :3] * 255).astype(np.uint8)
            if arr.dtype.kind == "f"
            else arr[opaque, :3]
        )
        assert np.allclose(actual_rgb, expected_rgb, atol=2)
        fig.savefig(io.BytesIO(), format="png")

    def test_logo_dpi_invariance_100_vs_300(self) -> None:
        fms.use_faser_style("faser")
        fracs: list[float] = []
        for dpi in (100, 300):
            fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=dpi)
            ax.plot([0, 1], [0, 1])
            artists = fms.draw_faser_logo(ax=ax, width=0.25, loc="upper left")
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()

            ab = next(a for a in artists if isinstance(a, AnnotationBbox))
            logo_bbox = ab.get_window_extent(renderer)
            ax_bbox = ax.get_window_extent(renderer)
            fracs.append(logo_bbox.width / ax_bbox.width)
            plt.close(fig)

        assert fracs[0] == pytest.approx(0.25, rel=0.06)
        assert fracs[1] == pytest.approx(0.25, rel=0.06)
        assert fracs[0] == pytest.approx(fracs[1], rel=0.03)


class TestAxisLabelAndYlimHelpers:
    def test_expand_ylim_linear_and_log(self) -> None:
        _fig1, ax1 = plt.subplots()
        ax1.set_ylim(10.0, 110.0)
        lo, hi = fms.expand_ylim(ax1, fraction=0.2, top=True, bottom=False)
        assert (lo, hi) == pytest.approx((10.0, 130.0))
        assert ax1.get_ylim() == pytest.approx((10.0, 130.0))

        lo_b, hi_b = fms.expand_ylim(ax1, fraction=0.25, top=False, bottom=True)
        assert (lo_b, hi_b) == pytest.approx((-20.0, 130.0))

        _fig2, ax2 = plt.subplots()
        ax2.set_yscale("log")
        ax2.set_ylim(1e1, 1e5)
        lo_log, hi_log = fms.expand_ylim(ax2, fraction=0.25, top=True, bottom=False)
        assert lo_log == pytest.approx(1e1)
        assert hi_log == pytest.approx(1e6)

        lo_log2, hi_log2 = fms.expand_ylim(ax2, fraction=0.2, top=False, bottom=True)
        assert lo_log2 == pytest.approx(1.0)
        assert hi_log2 == pytest.approx(1e6)

    def test_set_xlabel_and_ylabel_single_and_ratio_axes(self) -> None:
        fms.use_faser_style("faser")
        _fig, ax = plt.subplots()
        tx = fms.set_xlabel(r"$p_\mu\ [\mathrm{GeV}]$", ax=ax)
        ty = fms.set_ylabel("Events / bin", ax=ax)
        assert isinstance(tx, Text)
        assert isinstance(ty, Text)
        assert ax.get_xlabel() == r"$p_\mu\ [\mathrm{GeV}]$"
        assert ax.get_ylabel() == "Events / bin"

        # With ratio_axes, set_xlabel on main_ax forwards to bottom-most ratio axes
        fig_r, main_ax, ratio_ax = fms.ratio_axes()
        fms.set_xlabel(r"$E_\nu\ [\mathrm{GeV}]$", ax=main_ax)
        fms.set_ylabel("Events", ax=main_ax)
        fms.set_ylabel("Data / MC", ax=ratio_ax)

        assert main_ax.get_xlabel() == ""
        assert ratio_ax.get_xlabel() == r"$E_\nu\ [\mathrm{GeV}]$"
        assert main_ax.get_ylabel() == "Events"
        assert ratio_ax.get_ylabel() == "Data / MC"
        fig_r.savefig(io.BytesIO(), format="png")

        # Multi-ratio axes forwarding to bottom-most panel
        fig_m, main_m, ratio_list = fms.ratio_axes(extra_axes=1)
        fms.set_xlabel("x-axis", ax=main_m)
        assert main_m.get_xlabel() == ""
        assert ratio_list[0].get_xlabel() == ""
        assert ratio_list[-1].get_xlabel() == "x-axis"
        fig_m.savefig(io.BytesIO(), format="png")

    def test_set_zlabel_and_draw_tag(self) -> None:
        fms.use_faser_style("faser")
        fig, ax = plt.subplots()
        im = ax.pcolormesh([[1.0, 2.0], [3.0, 4.0]])
        cbar = fig.colorbar(im, ax=ax)

        zt = fms.set_zlabel("Efficiency", cbar)
        assert isinstance(zt, Text)
        assert cbar.ax.get_ylabel() == "Efficiency"

        tag = fms.draw_tag("v0.1.0 | internal", ax=ax)
        assert isinstance(tag, Text)
        assert tag.get_text() == "v0.1.0 | internal"
        fig.savefig(io.BytesIO(), format="png")
