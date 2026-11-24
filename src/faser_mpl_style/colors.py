"""Curated FASER Collaboration color palettes, semantic named colors, and 2D colormaps."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import matplotlib as mpl
from cycler import cycler
from matplotlib import colors as mcolors

if TYPE_CHECKING:
    from matplotlib.axes import Axes

FASER_COLORS: dict[str, str] = {
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

FASER_PALETTES: dict[str, list[str]] = {
    "faser": [
        "#0072B2",
        "#D55E00",
        "#009E73",
        "#E69F00",
        "#CC79A7",
        "#56B4E9",
        "#595959",
    ],
    "faser-tango": [
        "#3465A4",
        "#CC0000",
        "#F57900",
        "#4E9A06",
        "#75507B",
        "#729FCF",
    ],
    "faser-stack": [
        "#56B4E9",
        "#FF6B6B",
        "#7BC96F",
        "#FFB347",
        "#B39DDB",
        "#A9B4C2",
    ],
    "faser-classic": [
        "#0000FF",
        "#FF0000",
        "#009900",
        "#FFA500",
        "#9933CC",
        "#00AACC",
    ],
    "atlas": [
        "#D55E00",
        "#56B4E9",
        "#E69F00",
        "#F0E442",
        "#009E73",
        "#CC79A7",
        "#0072B2",
    ],
    "petroff6": [
        "#5790FC",
        "#F89C20",
        "#E42536",
        "#964A8B",
        "#9C9CA1",
        "#7A21DD",
    ],
    "petroff8": [
        "#1845FB",
        "#FF5E02",
        "#C91F16",
        "#C849A9",
        "#ADAD7D",
        "#86C8DD",
        "#578DFF",
        "#656364",
    ],
    "petroff10": [
        "#3F90DA",
        "#FFA90E",
        "#BD1F01",
        "#94A4A2",
        "#832DB6",
        "#A96B59",
        "#E76300",
        "#B9AC70",
        "#717581",
        "#92DADD",
    ],
}

_BIRD_STOPS: list[tuple[float, str]] = [
    (0.000, "#263EA8"),
    (0.111, "#1652CD"),
    (0.222, "#1064DC"),
    (0.333, "#1272D9"),
    (0.444, "#1481D6"),
    (0.556, "#0E8FD1"),
    (0.667, "#099DCC"),
    (0.778, "#2EB7A4"),
    (0.889, "#95BE71"),
    (0.944, "#D1BB59"),
    (1.000, "#F9F90F"),
]

_BLUES_STOPS: list[tuple[float, str]] = [
    (0.00, "#FFFFFF"),
    (0.15, "#D4E6F6"),
    (0.35, "#7FB3D5"),
    (0.60, "#2E86C1"),
    (0.82, "#1B4F72"),
    (1.00, "#0B2545"),
]


def get_palette(name: str = "faser", n: int | None = None) -> list[str]:
    """Return a list of hex colors for a named FASER palette.

    Parameters
    ----------
    name:
        Palette name from :data:`FASER_PALETTES` (case-insensitive). Also
        accepts ``"petroff"`` to automatically select ``petroff6``,
        ``petroff8``, or ``petroff10`` based on ``n``.
    n:
        Optional number of colors to return. When ``name == "faser"`` and
        ``n > 7``, automatically upgrades to ``petroff8`` (``n == 8``) or
        ``petroff10`` (``n >= 9``). If ``n`` exceeds the palette length,
        colors are cycled.

    Returns
    -------
    list[str]
        List of hex color strings.
    """
    if n is not None and n < 0:
        raise ValueError(f"Number of colors n must be non-negative, got {n}.")
    if n == 0:
        return []

    key = name.strip().lower()
    if key == "petroff":
        if n is None or n <= 6:
            base = FASER_PALETTES["petroff6"]
        elif n <= 8:
            base = FASER_PALETTES["petroff8"]
        else:
            base = FASER_PALETTES["petroff10"]
    elif key == "faser":
        if n is None or n <= 7:
            base = FASER_PALETTES["faser"]
        elif n == 8:
            base = FASER_PALETTES["petroff8"]
        else:
            base = FASER_PALETTES["petroff10"]
    elif key in FASER_PALETTES:
        base = FASER_PALETTES[key]
    else:
        available = ", ".join(sorted(FASER_PALETTES))
        raise ValueError(f"Unknown palette {name!r}. Available palettes: {available}.")

    if n is None:
        return list(base)
    if n <= len(base):
        return list(base[:n])
    return [base[i % len(base)] for i in range(n)]


def set_color_cycle(
    palette: str | Sequence[str] = "faser",
    n: int | None = None,
    *,
    ax: Axes | None = None,
) -> list[str]:
    """Set Matplotlib's ``axes.prop_cycle`` globally or on a specific axes.

    Parameters
    ----------
    palette:
        Named palette from :data:`FASER_PALETTES` or an explicit sequence of
        Matplotlib color specifications.
    n:
        Optional number of colors to take (or cycle to).
    ax:
        If provided, applies the cycle only to ``ax``; otherwise updates
        global ``matplotlib.rcParams["axes.prop_cycle"]``.

    Returns
    -------
    list[str]
        The resolved list of colors applied.
    """
    if isinstance(palette, str):
        colors = get_palette(palette, n=n)
    else:
        colors = list(palette)
        if not colors:
            raise ValueError("Custom color palette must contain at least one color.")
        if n is not None:
            if n < 0:
                raise ValueError(f"Number of colors n must be non-negative, got {n}.")
            colors = [colors[i % len(colors)] for i in range(n)] if n > 0 else []

    if not colors:
        raise ValueError("Resolved color cycle cannot be empty.")

    prop_cycle = cycler(color=colors)
    if ax is None:
        mpl.rcParams["axes.prop_cycle"] = prop_cycle
    else:
        ax.set_prop_cycle(prop_cycle)
    return colors


def register_colors() -> None:
    """Register all ``faser:<name>`` colors into Matplotlib's named color table."""
    mapping = mcolors.get_named_colors_mapping()
    for name, hex_color in FASER_COLORS.items():
        mapping[f"faser:{name}"] = hex_color


def register_colormaps() -> None:
    """Register ``faser_bird``, ``faser_blues``, their reversed variants, and ``bird``."""
    bird_cmap = mcolors.LinearSegmentedColormap.from_list("faser_bird", _BIRD_STOPS, N=256)
    blues_cmap = mcolors.LinearSegmentedColormap.from_list("faser_blues", _BLUES_STOPS, N=256)

    to_register: list[tuple[str, mcolors.Colormap]] = [
        ("faser_bird", bird_cmap),
        ("faser_bird_r", bird_cmap.reversed("faser_bird_r")),
        ("faser_blues", blues_cmap),
        ("faser_blues_r", blues_cmap.reversed("faser_blues_r")),
    ]
    for cmap_name, cmap_obj in to_register:
        if cmap_name not in mpl.colormaps:
            mpl.colormaps.register(cmap_obj, name=cmap_name)

    if "bird" not in mpl.colormaps:
        mpl.colormaps.register(bird_cmap.copy(), name="bird")
    if "bird_r" not in mpl.colormaps:
        mpl.colormaps.register(bird_cmap.reversed("bird_r"), name="bird_r")
