"""Stylesheet loading, global style configuration, context managers, and font helpers."""

from __future__ import annotations

import shutil
import warnings
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Any, Literal

import matplotlib as mpl
import matplotlib.style as mpl_style

from .colors import register_colormaps, register_colors, set_color_cycle

STYLES: tuple[str, ...] = (
    "faser",
    "faser-square",
    "faser-talk",
    "faser-atlas-compat",
)

_SCALED_FONT_KEYS: tuple[str, ...] = (
    "font.size",
    "axes.titlesize",
    "axes.labelsize",
    "xtick.labelsize",
    "ytick.labelsize",
    "legend.fontsize",
    "legend.title_fontsize",
    "figure.titlesize",
    "figure.labelsize",
)

_LATEX_PREAMBLE = (
    r"\usepackage{amsmath}"
    r"\usepackage{amssymb}"
    r"\usepackage{helvet}"
    r"\renewcommand{\familydefault}{\sfdefault}"
)


def get_style_dict(preset: str = "faser") -> dict[str, Any]:
    """Load and return a preset stylesheet as a plain ``rcParams`` dictionary.

    Does not mutate Matplotlib's global ``rcParams``.

    Parameters
    ----------
    preset:
        One of :data:`STYLES` or a filesystem path to a custom ``.mplstyle`` file.
    """
    if preset in STYLES:
        style_ref = resources.files("faser_mpl_style").joinpath(f"{preset}.mplstyle")
        with resources.as_file(style_ref) as style_path:
            loaded = mpl.rc_params_from_file(
                str(style_path), fail_on_error=True, use_default_template=False
            )
        return {str(k): v for k, v in loaded.items()}

    custom_path = Path(preset)
    if custom_path.is_file():
        loaded = mpl.rc_params_from_file(
            str(custom_path), fail_on_error=True, use_default_template=False
        )
        return {str(k): v for k, v in loaded.items()}

    available = ", ".join(STYLES)
    raise ValueError(
        f"Unknown style preset {preset!r}. Expected one of ({available}) "
        "or a path to an existing .mplstyle file."
    )


def _configure_usetex() -> None:
    """Enable ``text.usetex`` if external TeX tools are available; otherwise warn and fall back."""
    missing: list[str] = []
    if shutil.which("pdflatex") is None and shutil.which("latex") is None:
        missing.append("pdflatex/latex")
    if shutil.which("dvipng") is None:
        missing.append("dvipng")
    if shutil.which("gs") is None:
        missing.append("gs")

    if missing:
        warnings.warn(
            "LaTeX rendering requested (usetex=True), but required external tool(s) "
            f"were not found on PATH: {', '.join(missing)}. "
            "Falling back to Matplotlib mathtext (text.usetex=False).",
            UserWarning,
            stacklevel=3,
        )
        mpl.rcParams["text.usetex"] = False
        return

    mpl.rcParams["text.usetex"] = True
    mpl.rcParams["text.latex.preamble"] = _LATEX_PREAMBLE


def set_font(
    family: str | Sequence[str] | None = None,
    size: float | None = None,
) -> None:
    """Prepend font family(ies) to ``font.sans-serif`` and/or proportionally scale font sizes.

    Parameters
    ----------
    family:
        Font family name or sequence of names to prepend to ``rcParams["font.sans-serif"]``.
    size:
        New base ``rcParams["font.size"]`` in points. All numeric font-size
        ``rcParams`` are scaled proportionally by ``size / current_font_size``.
    """
    if family is not None:
        if mpl.rcParams.get("text.usetex", False):
            warnings.warn(
                "set_font(family=...) has no effect on TeX fonts while text.usetex=True.",
                UserWarning,
                stacklevel=2,
            )
        families = [family] if isinstance(family, str) else list(family)
        existing = list(mpl.rcParams.get("font.sans-serif", []))
        merged: list[str] = []
        for item in families + existing:
            if item not in merged:
                merged.append(item)
        mpl.rcParams["font.sans-serif"] = merged

    if size is not None:
        target = float(size)
        if target <= 0.0:
            raise ValueError(f"Font size must be positive, got {size}.")
        current_base = float(mpl.rcParams["font.size"])
        scale = target / current_base
        rc_params: Any = mpl.rcParams
        for key in _SCALED_FONT_KEYS:
            if key == "font.size":
                rc_params[key] = target
                continue
            if key in rc_params:
                val = rc_params[key]
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    rc_params[key] = float(val) * scale


def use_faser_style(
    preset: str = "faser",
    *,
    palette: str | Sequence[str] | None = None,
    usetex: bool = False,
    ticks: Literal["all", "bl"] | None = None,
    minor_ticks: bool | None = None,
    fancy_legend: bool = False,
    font_size: float | None = None,
    figsize: tuple[float, float] | None = None,
    rc: Mapping[str, Any] | None = None,
) -> None:
    """Apply a FASER Matplotlib style preset globally with optional overrides.

    Parameters
    ----------
    preset:
        One of :data:`STYLES` or a path to a custom ``.mplstyle`` file.
    palette:
        Palette name from :data:`~faser_mpl_style.FASER_PALETTES` or explicit color sequence.
    usetex:
        If ``True``, enables LaTeX rendering when ``pdflatex``/``latex``, ``dvipng``,
        and ``gs`` are available on ``PATH``; otherwise warns and keeps mathtext.
    ticks:
        ``"all"`` enables top and right ticks; ``"bl"`` restricts ticks to bottom and left.
        When ``None``, preserves the chosen stylesheet's default (``"all"`` for ``faser``,
        ``faser-square``, and ``faser-talk``; ``"bl"`` for ``faser-atlas-compat``).
    minor_ticks:
        If not ``None``, overrides ``xtick.minor.visible`` and ``ytick.minor.visible``.
    fancy_legend:
        If ``True``, enables rounded legend frames (``legend.frameon`` and ``legend.fancybox``).
    font_size:
        If given, proportionally scales all font sizes via :func:`set_font`.
    figsize:
        If given, overrides ``figure.figsize``.
    rc:
        Optional mapping of arbitrary ``rcParams`` applied last.
    """
    if ticks is not None and ticks not in ("all", "bl"):
        raise ValueError(f"Unknown ticks option {ticks!r}; expected 'all', 'bl', or None.")

    style_dict = get_style_dict(preset)
    register_colors()
    register_colormaps()

    mpl_style.use(style_dict)

    if palette is not None:
        set_color_cycle(palette)

    if ticks == "all":
        mpl.rcParams["xtick.top"] = True
        mpl.rcParams["ytick.right"] = True
    elif ticks == "bl":
        mpl.rcParams["xtick.top"] = False
        mpl.rcParams["ytick.right"] = False

    if minor_ticks is not None:
        mpl.rcParams["xtick.minor.visible"] = bool(minor_ticks)
        mpl.rcParams["ytick.minor.visible"] = bool(minor_ticks)

    if fancy_legend:
        mpl.rcParams["legend.frameon"] = True
        mpl.rcParams["legend.fancybox"] = True

    if usetex:
        _configure_usetex()

    if font_size is not None:
        set_font(size=font_size)

    if figsize is not None:
        mpl.rcParams["figure.figsize"] = [float(figsize[0]), float(figsize[1])]

    if rc is not None:
        rc_params: Any = mpl.rcParams
        rc_params.update(dict(rc))


@contextmanager
def style_context(
    preset: str = "faser",
    *,
    palette: str | Sequence[str] | None = None,
    usetex: bool = False,
    ticks: Literal["all", "bl"] | None = None,
    minor_ticks: bool | None = None,
    fancy_legend: bool = False,
    font_size: float | None = None,
    figsize: tuple[float, float] | None = None,
    rc: Mapping[str, Any] | None = None,
) -> Iterator[None]:
    """Context manager applying :func:`use_faser_style` temporarily and restoring ``rcParams`` on exit."""
    with mpl.rc_context():
        use_faser_style(
            preset=preset,
            palette=palette,
            usetex=usetex,
            ticks=ticks,
            minor_ticks=minor_ticks,
            fancy_legend=fancy_legend,
            font_size=font_size,
            figsize=figsize,
            rc=rc,
        )
        yield


def reset_style() -> None:
    """Restore Matplotlib default ``rcParams``."""
    mpl.rcdefaults()
