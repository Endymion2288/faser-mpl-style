from __future__ import annotations

import io
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

import faser_mpl_style as fms


class TestStylesAndPresets:
    def test_styles_constant(self) -> None:
        assert fms.STYLES == ("faser", "faser-square", "faser-talk", "faser-atlas-compat")

    def test_use_faser_default_preset(self) -> None:
        fms.use_faser_style("faser")
        rc = matplotlib.rcParams

        assert list(rc["figure.figsize"]) == pytest.approx([8.0, 6.0])
        assert rc["figure.dpi"] == 150
        assert rc["savefig.dpi"] == 300
        assert rc["figure.facecolor"] == "white"
        assert rc["savefig.facecolor"] == "white"

        assert rc["font.family"] == ["sans-serif"]
        assert rc["font.size"] == pytest.approx(15.0)
        assert rc["axes.labelsize"] == pytest.approx(18.0)
        assert rc["xtick.labelsize"] == pytest.approx(15.0)
        assert rc["ytick.labelsize"] == pytest.approx(15.0)
        assert rc["legend.fontsize"] == pytest.approx(14.0)

        assert rc["text.usetex"] is False
        assert rc["mathtext.fontset"] == "custom"
        assert rc["mathtext.rm"] == "sans"
        assert rc["mathtext.sf"] == "sans"
        assert rc["mathtext.it"] == "sans:italic"
        assert rc["mathtext.bf"] == "sans:bold"
        assert rc["mathtext.default"] == "it"
        assert rc["mathtext.fallback"] == "stixsans"

        assert rc["axes.linewidth"] == pytest.approx(1.0)
        assert rc["axes.grid"] is False
        assert rc["xaxis.labellocation"] == "right"
        assert rc["yaxis.labellocation"] == "top"

        assert rc["xtick.top"] is True
        assert rc["ytick.right"] is True
        assert rc["xtick.direction"] == "in"
        assert rc["ytick.direction"] == "in"
        assert rc["xtick.major.size"] == pytest.approx(8.0)
        assert rc["xtick.minor.size"] == pytest.approx(4.0)
        assert rc["ytick.major.size"] == pytest.approx(8.0)
        assert rc["ytick.minor.size"] == pytest.approx(4.0)
        assert rc["xtick.minor.visible"] is True
        assert rc["ytick.minor.visible"] is True

        assert rc["lines.linewidth"] == pytest.approx(1.8)
        assert rc["lines.markersize"] == pytest.approx(6.5)
        assert rc["errorbar.capsize"] == pytest.approx(0.0)
        assert rc["legend.frameon"] is False
        assert rc["image.cmap"] == "viridis"

    def test_use_faser_square_preset(self) -> None:
        fms.use_faser_style("faser-square")
        rc = matplotlib.rcParams

        assert list(rc["figure.figsize"]) == pytest.approx([6.0, 6.0])
        assert rc["figure.subplot.left"] == pytest.approx(0.16)
        assert rc["figure.subplot.bottom"] == pytest.approx(0.16)
        assert rc["xtick.major.size"] == pytest.approx(7.0)
        assert rc["xtick.minor.size"] == pytest.approx(3.5)
        assert rc["font.size"] == pytest.approx(15.0)
        assert rc["xtick.top"] is True
        assert rc["ytick.right"] is True

    def test_use_faser_talk_preset(self) -> None:
        fms.use_faser_style("faser-talk")
        rc = matplotlib.rcParams

        assert list(rc["figure.figsize"]) == pytest.approx([8.0, 5.5])
        assert rc["font.size"] == pytest.approx(17.0)
        assert rc["axes.labelsize"] == pytest.approx(20.0)
        assert rc["xtick.labelsize"] == pytest.approx(17.0)
        assert rc["legend.fontsize"] == pytest.approx(16.0)
        assert rc["axes.linewidth"] == pytest.approx(1.2)
        assert rc["lines.linewidth"] == pytest.approx(2.2)
        assert rc["lines.markersize"] == pytest.approx(7.5)

    def test_faser_atlas_compat_preset(self) -> None:
        style_dict = fms.get_style_dict("faser-atlas-compat")
        assert list(style_dict["figure.figsize"]) == pytest.approx([6.0, 6.0])
        assert style_dict["font.size"] == pytest.approx(18.0)
        assert style_dict["axes.labelsize"] == pytest.approx(20.0)
        assert style_dict["xaxis.labellocation"] == "center"
        assert style_dict["yaxis.labellocation"] == "center"
        assert style_dict["xtick.top"] is False
        assert style_dict["ytick.right"] is False
        assert style_dict["xtick.minor.visible"] is False
        assert style_dict["ytick.minor.visible"] is False
        assert style_dict["mathtext.fontset"] == "custom"

        fms.use_faser_style("faser-atlas-compat", ticks="bl")
        assert list(matplotlib.rcParams["figure.figsize"]) == pytest.approx([6.0, 6.0])
        assert matplotlib.rcParams["xtick.top"] is False
        assert matplotlib.rcParams["ytick.right"] is False
        assert matplotlib.rcParams["xtick.minor.visible"] is False

    @pytest.mark.parametrize("preset", fms.STYLES)
    def test_get_style_dict_does_not_mutate_rcparams(self, preset: str) -> None:
        orig_size = matplotlib.rcParams["font.size"]
        orig_figsize = list(matplotlib.rcParams["figure.figsize"])

        d = fms.get_style_dict(preset)
        assert isinstance(d, dict)
        assert "font.size" in d
        assert matplotlib.rcParams["font.size"] == orig_size
        assert list(matplotlib.rcParams["figure.figsize"]) == orig_figsize

        # Mutating returned dict does not affect subsequent calls or rcParams
        d["font.size"] = 999.0
        assert fms.get_style_dict(preset)["font.size"] != 999.0
        assert matplotlib.rcParams["font.size"] == orig_size

    def test_unknown_preset_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="not-a-real-preset"):
            fms.use_faser_style("not-a-real-preset")

        with pytest.raises(ValueError, match="not-a-real-preset"):
            fms.get_style_dict("not-a-real-preset")

    def test_custom_mplstyle_file_path(self, tmp_path: Path) -> None:
        custom_style = tmp_path / "custom_faser.mplstyle"
        custom_style.write_text("lines.linewidth: 3.25\naxes.grid: True\n", encoding="utf-8")

        fms.use_faser_style(str(custom_style))
        assert matplotlib.rcParams["lines.linewidth"] == pytest.approx(3.25)
        assert matplotlib.rcParams["axes.grid"] is True


class TestStyleOverridesAndContext:
    def test_ticks_minor_ticks_fancy_legend_figsize_rc(self) -> None:
        fms.use_faser_style(
            "faser",
            ticks="bl",
            minor_ticks=False,
            fancy_legend=True,
            figsize=(9.5, 4.5),
            palette="faser-tango",
            rc={"axes.grid": True, "lines.linewidth": 2.75},
        )
        rc = matplotlib.rcParams
        assert rc["xtick.top"] is False
        assert rc["ytick.right"] is False
        assert rc["xtick.minor.visible"] is False
        assert rc["ytick.minor.visible"] is False
        assert rc["legend.frameon"] is True
        assert rc["legend.fancybox"] is True
        assert list(rc["figure.figsize"]) == pytest.approx([9.5, 4.5])
        assert rc["axes.grid"] is True
        assert rc["lines.linewidth"] == pytest.approx(2.75)

        cycle_colors = [c.upper() for c in rc["axes.prop_cycle"].by_key()["color"]]
        expected = [c.upper() for c in fms.FASER_PALETTES["faser-tango"]]
        assert cycle_colors == expected

    def test_ticks_all_and_minor_ticks_true(self) -> None:
        fms.use_faser_style("faser-atlas-compat", ticks="all", minor_ticks=True)
        assert matplotlib.rcParams["xtick.top"] is True
        assert matplotlib.rcParams["ytick.right"] is True
        assert matplotlib.rcParams["xtick.minor.visible"] is True
        assert matplotlib.rcParams["ytick.minor.visible"] is True

    def test_style_context_restores_on_exit(self) -> None:
        orig_fontsize = matplotlib.rcParams["font.size"]
        orig_figsize = list(matplotlib.rcParams["figure.figsize"])
        orig_grid = matplotlib.rcParams["axes.grid"]

        with fms.style_context("faser-talk", figsize=(10.0, 4.0), rc={"axes.grid": True}):
            assert matplotlib.rcParams["font.size"] == pytest.approx(17.0)
            assert list(matplotlib.rcParams["figure.figsize"]) == pytest.approx([10.0, 4.0])
            assert matplotlib.rcParams["axes.grid"] is True

        assert matplotlib.rcParams["font.size"] == orig_fontsize
        assert list(matplotlib.rcParams["figure.figsize"]) == orig_figsize
        assert matplotlib.rcParams["axes.grid"] == orig_grid

    def test_style_context_restores_on_exception(self) -> None:
        orig_fontsize = matplotlib.rcParams["font.size"]
        orig_lw = matplotlib.rcParams["lines.linewidth"]

        with (
            pytest.raises(RuntimeError, match="boom"),
            fms.style_context("faser-talk", rc={"lines.linewidth": 4.2}),
        ):
            assert matplotlib.rcParams["lines.linewidth"] == pytest.approx(4.2)
            raise RuntimeError("boom")

        assert matplotlib.rcParams["font.size"] == orig_fontsize
        assert matplotlib.rcParams["lines.linewidth"] == orig_lw

    def test_reset_style_restores_defaults(self) -> None:
        fms.use_faser_style("faser-talk")
        assert matplotlib.rcParams["font.size"] == pytest.approx(17.0)
        fms.reset_style()
        assert matplotlib.rcParams["font.size"] == matplotlib.rcParamsDefault["font.size"]
        assert list(matplotlib.rcParams["figure.figsize"]) == list(
            matplotlib.rcParamsDefault["figure.figsize"]
        )


class TestSetFontAndUsetex:
    def test_set_font_proportional_scaling(self) -> None:
        fms.use_faser_style("faser")
        scale = 18.0 / 15.0
        before = {
            key: matplotlib.rcParams[key]
            for key in (
                "font.size",
                "axes.titlesize",
                "axes.labelsize",
                "xtick.labelsize",
                "ytick.labelsize",
                "legend.fontsize",
                "legend.title_fontsize",
                "figure.titlesize",
            )
        }

        fms.set_font(size=18.0)

        for key, old_val in before.items():
            assert matplotlib.rcParams[key] == pytest.approx(old_val * scale)

    def test_use_faser_style_font_size_kwarg(self) -> None:
        fms.use_faser_style("faser", font_size=12.0)
        assert matplotlib.rcParams["font.size"] == pytest.approx(12.0)
        assert matplotlib.rcParams["axes.labelsize"] == pytest.approx(18.0 * (12.0 / 15.0))
        assert matplotlib.rcParams["legend.fontsize"] == pytest.approx(14.0 * (12.0 / 15.0))

    def test_set_font_family_prepends(self) -> None:
        fms.use_faser_style("faser")
        fms.set_font(family="CustomSansTest")
        assert matplotlib.rcParams["font.sans-serif"][0] == "CustomSansTest"
        assert "DejaVu Sans" in matplotlib.rcParams["font.sans-serif"]

        fms.set_font(family=["FirstFont", "SecondFont"])
        assert matplotlib.rcParams["font.sans-serif"][:2] == ["FirstFont", "SecondFont"]

    def test_set_font_family_warns_when_usetex_enabled(self) -> None:
        fms.use_faser_style("faser")
        matplotlib.rcParams["text.usetex"] = True
        with pytest.warns(UserWarning, match="usetex"):
            fms.set_font(family="Helvetica")

    def test_usetex_missing_binaries_warns_and_falls_back(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(shutil, "which", lambda _cmd: None)
        with pytest.warns(UserWarning):
            fms.use_faser_style("faser", usetex=True)
        assert matplotlib.rcParams["text.usetex"] is False

    def test_usetex_partial_missing_binary_warns_and_falls_back(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            shutil,
            "which",
            lambda cmd: "/usr/bin/pdflatex" if cmd in {"pdflatex", "latex"} else None,
        )
        with pytest.warns(UserWarning):
            fms.use_faser_style("faser", usetex=True)
        assert matplotlib.rcParams["text.usetex"] is False

    def test_usetex_all_binaries_available_enables_usetex(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
        fms.use_faser_style("faser", usetex=True)
        assert matplotlib.rcParams["text.usetex"] is True
        preamble = matplotlib.rcParams["text.latex.preamble"]
        assert "amsmath" in preamble


class TestSubprocessDiscoveryAndMinimalFonts:
    @pytest.mark.parametrize("preset", fms.STYLES)
    def test_zero_import_dotted_style_discovery_subprocess(self, preset: str) -> None:
        code = (
            "import io, sys, matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "assert 'faser_mpl_style' not in sys.modules\n"
            f"plt.style.use('faser_mpl_style.{preset}')\n"
            "assert matplotlib.rcParams['mathtext.fontset'] == 'custom'\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot([0, 1, 2], [1, 4, 2], label=r'$p_\\mu$')\n"
            "ax.set_xlabel(r'$E_\\nu\\ [\\mathrm{GeV}]$')\n"
            "ax.set_ylabel('Events')\n"
            "ax.legend()\n"
            "buf = io.BytesIO()\n"
            "fig.savefig(buf, format='png')\n"
            "assert len(buf.getvalue()) > 1000\n"
        )
        result = subprocess.run(
            [sys.executable, "-W", "error::UserWarning", "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"

    @pytest.mark.parametrize("preset", fms.STYLES)
    def test_post_import_short_name_style_discovery_subprocess(self, preset: str) -> None:
        code = (
            "import io, matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "import faser_mpl_style\n"
            f"plt.style.use('{preset}')\n"
            "assert matplotlib.rcParams['mathtext.fontset'] == 'custom'\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot([0, 1, 2], [2, 3, 5], label=r'$\\sqrt{s}=13.6\\ \\mathrm{TeV}$')\n"
            "ax.set_xlabel(r'$m_{A\\prime}\\ [\\mathrm{MeV}]$')\n"
            "ax.set_ylabel('Events')\n"
            "ax.legend()\n"
            "buf = io.BytesIO()\n"
            "fig.savefig(buf, format='png')\n"
            "assert len(buf.getvalue()) > 1000\n"
        )
        result = subprocess.run(
            [sys.executable, "-W", "error::UserWarning", "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"

    def test_minimal_dejavu_only_linux_font_rendering_zero_warnings(self) -> None:
        fms.use_faser_style("faser")
        matplotlib.rcParams["font.sans-serif"] = ["NonExistentFontXYZ", "DejaVu Sans"]

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            fig, ax = plt.subplots()
            ax.plot([1, 10, 100], [10, 100, 1000], label=r"$\nu_\mu$ CC ($\pm 1\sigma \oplus \mathrm{syst.}$)")
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(r"$p_\mu\ [\mathrm{GeV}]$")
            ax.set_ylabel(r"$\mathrm{d}\sigma/\mathrm{d}E_\nu\ [\mathrm{fb}/\mathrm{GeV}]$")
            ax.text(
                0.05,
                0.90,
                r"$\mathbfit{FASER}\nu$ Preliminary" + "\n" + r"$\sqrt{s} = 13.6\ \mathrm{TeV},\ \mathcal{L} = 186\ \mathrm{fb}^{-1}$",
                transform=ax.transAxes,
            )
            ax.legend()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")

        assert len(buf.getvalue()) > 1000
        user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
        assert user_warnings == [], [str(w.message) for w in user_warnings]
