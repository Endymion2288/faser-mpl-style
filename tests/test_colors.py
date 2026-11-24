from __future__ import annotations

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pytest

import faser_mpl_style as fms

EXPECTED_PALETTE_NAMES = (
    "faser",
    "faser-tango",
    "faser-stack",
    "faser-classic",
    "atlas",
    "petroff6",
    "petroff8",
    "petroff10",
)

EXPECTED_FASER_COLORS: dict[str, str] = {
    "blue": "#0072B2",
    "red": "#D55E00",
    "green": "#009E73",
    "orange": "#E69F00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "coral": "#FF6B6B",
    "gray": "#595959",
    "tango-blue": "#3465A4",
    "tango-red": "#CC0000",
    "tango-orange": "#F57900",
    "data": "#000000",
    "obs-limit": "#0033FF",
    "exp-limit": "#333333",
    "onesigma": "#B9FF61",
    "twosigma": "#FFF57A",
    "atlas-onesigma": "#00FF26",
    "atlas-twosigma": "#FBFF1F",
    "existing-fill": "#D9D9D9",
    "existing-edge": "#8C8C8C",
    "existing-text": "#666666",
    "unc-band": "#7F7F7F",
}


class TestPalettes:
    def test_all_eight_palettes_defined_and_valid(self) -> None:
        assert set(fms.FASER_PALETTES.keys()) == set(EXPECTED_PALETTE_NAMES)
        for name, colors in fms.FASER_PALETTES.items():
            assert len(colors) >= 6, f"Palette {name!r} unexpectedly short"
            for color in colors:
                assert mcolors.is_color_like(color), f"Invalid color {color!r} in {name!r}"

        assert [c.upper() for c in fms.FASER_PALETTES["faser"][:2]] == ["#0072B2", "#D55E00"]
        assert len(fms.FASER_PALETTES["faser"]) == 7
        assert len(fms.FASER_PALETTES["faser-tango"]) == 6
        assert len(fms.FASER_PALETTES["faser-stack"]) == 6
        assert len(fms.FASER_PALETTES["faser-classic"]) == 6
        assert len(fms.FASER_PALETTES["atlas"]) == 7
        assert len(fms.FASER_PALETTES["petroff6"]) == 6
        assert len(fms.FASER_PALETTES["petroff8"]) == 8
        assert len(fms.FASER_PALETTES["petroff10"]) == 10

    def test_get_palette_default_and_copy(self) -> None:
        pal = fms.get_palette()
        assert pal == fms.FASER_PALETTES["faser"]
        pal.append("#123456")
        assert len(fms.FASER_PALETTES["faser"]) == 7

    def test_get_palette_case_insensitive(self) -> None:
        assert fms.get_palette("FASER") == fms.FASER_PALETTES["faser"]
        assert fms.get_palette("Faser-Tango") == fms.FASER_PALETTES["faser-tango"]
        assert fms.get_palette("ATLAS") == fms.FASER_PALETTES["atlas"]
        assert fms.get_palette("PETROFF8") == fms.FASER_PALETTES["petroff8"]

    def test_get_palette_faser_auto_scaling(self) -> None:
        assert fms.get_palette("faser", n=4) == fms.FASER_PALETTES["faser"][:4]
        assert fms.get_palette("faser", n=7) == fms.FASER_PALETTES["faser"]
        assert fms.get_palette("faser", n=8) == fms.FASER_PALETTES["petroff8"]
        assert fms.get_palette("faser", n=9) == fms.FASER_PALETTES["petroff10"][:9]
        assert fms.get_palette("faser", n=10) == fms.FASER_PALETTES["petroff10"]

        pal12 = fms.get_palette("faser", n=12)
        assert len(pal12) == 12
        assert pal12[:10] == fms.FASER_PALETTES["petroff10"]
        assert pal12[10:12] == fms.FASER_PALETTES["petroff10"][:2]

    def test_get_palette_petroff_alias(self) -> None:
        assert fms.get_palette("Petroff", n=4) == fms.FASER_PALETTES["petroff6"][:4]
        assert fms.get_palette("Petroff", n=6) == fms.FASER_PALETTES["petroff6"]
        assert fms.get_palette("petroff", n=7) == fms.FASER_PALETTES["petroff8"][:7]
        assert fms.get_palette("petroff", n=8) == fms.FASER_PALETTES["petroff8"]
        assert fms.get_palette("Petroff", n=9) == fms.FASER_PALETTES["petroff10"][:9]
        assert fms.get_palette("Petroff", n=10) == fms.FASER_PALETTES["petroff10"]

        pal12 = fms.get_palette("Petroff", n=12)
        assert len(pal12) == 12
        assert pal12[10:] == fms.FASER_PALETTES["petroff10"][:2]

    def test_get_palette_cyclic_repeat(self) -> None:
        pal = fms.get_palette("faser-tango", n=9)
        base = fms.FASER_PALETTES["faser-tango"]
        assert len(pal) == 9
        assert pal[:6] == base
        assert pal[6:] == base[:3]

    def test_get_palette_unknown_raises(self) -> None:
        with pytest.raises((KeyError, ValueError), match="nonexistent-palette"):
            fms.get_palette("nonexistent-palette")


class TestColorCycle:
    def test_set_color_cycle_global(self) -> None:
        applied = fms.set_color_cycle("faser-stack", n=4)
        assert applied == fms.FASER_PALETTES["faser-stack"][:4]
        rc_colors = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
        assert [c.upper() for c in rc_colors] == [c.upper() for c in applied]

    def test_set_color_cycle_per_axes_does_not_mutate_global(self) -> None:
        orig_global = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
        _fig, ax = plt.subplots()
        custom = ["#112233", "#445566", "#778899"]
        applied = fms.set_color_cycle(custom, ax=ax)

        assert applied == custom
        assert matplotlib.rcParams["axes.prop_cycle"].by_key()["color"] == orig_global

        lines = [ax.plot([0, 1], [i, i + 1])[0] for i in range(3)]
        assert [mcolors.to_hex(ln.get_color()).upper() for ln in lines] == custom


class TestNamedColorsAndColormaps:
    def test_all_22_named_colors_registered(self) -> None:
        assert len(fms.FASER_COLORS) == 22
        assert {k: v.upper() for k, v in fms.FASER_COLORS.items()} == EXPECTED_FASER_COLORS

        named = mcolors.get_named_colors_mapping()
        for key, expected_hex in EXPECTED_FASER_COLORS.items():
            full_name = f"faser:{key}"
            assert full_name in named, f"{full_name} missing from Matplotlib named colors"
            assert mcolors.to_hex(full_name).upper() == expected_hex

    def test_register_colors_is_idempotent(self) -> None:
        fms.register_colors()
        fms.register_colors()
        assert mcolors.to_hex("faser:blue").upper() == "#0072B2"
        assert mcolors.to_hex("faser:onesigma").upper() == "#B9FF61"

    @pytest.mark.parametrize(
        "cmap_name",
        ("faser_bird", "faser_bird_r", "faser_blues", "faser_blues_r", "bird"),
    )
    def test_colormaps_registered_and_usable(self, cmap_name: str) -> None:
        assert cmap_name in matplotlib.colormaps
        cmap = matplotlib.colormaps[cmap_name]
        sample = cmap(np.linspace(0.0, 1.0, 5))
        assert sample.shape == (5, 4)
        assert np.all(np.isfinite(sample))

    def test_colormap_endpoints(self) -> None:
        bird = matplotlib.colormaps["faser_bird"]
        bird_r = matplotlib.colormaps["faser_bird_r"]
        assert mcolors.to_hex(bird(0.0)).upper() == "#263EA8"
        assert mcolors.to_hex(bird(1.0)).upper() == "#F9F90F"
        assert np.allclose(bird(0.0), bird_r(1.0), atol=1e-2)
        assert np.allclose(bird(1.0), bird_r(0.0), atol=1e-2)

        blues = matplotlib.colormaps["faser_blues"]
        blues_r = matplotlib.colormaps["faser_blues_r"]
        assert mcolors.to_hex(blues(0.0)).upper() == "#FFFFFF"
        assert mcolors.to_hex(blues(1.0)).upper() == "#0B2545"
        assert np.allclose(blues(0.0), blues_r(1.0), atol=1e-2)
        assert np.allclose(blues(1.0), blues_r(0.0), atol=1e-2)

    def test_register_colormaps_is_idempotent(self) -> None:
        fms.register_colormaps()
        fms.register_colormaps()
        assert "faser_bird" in matplotlib.colormaps
        assert "faser_blues" in matplotlib.colormaps
