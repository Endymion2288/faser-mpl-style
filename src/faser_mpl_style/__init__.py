"""FASER Collaboration Matplotlib stylesheets, color palettes, and publication plotting helpers."""

from __future__ import annotations

import atexit
from contextlib import ExitStack
from importlib import resources

import matplotlib.style as mpl_style

from ._version import __version__
from .colors import (
    FASER_COLORS,
    FASER_PALETTES,
    get_palette,
    register_colormaps,
    register_colors,
    set_color_cycle,
)
from .labels import (
    STATUS_ALIASES,
    draw_faser_label,
    draw_faser_logo,
    draw_tag,
    expand_ylim,
    set_xlabel,
    set_ylabel,
    set_zlabel,
)
from .plot import (
    plot_1d,
    plot_2d,
    plot_band,
    plot_data,
    plot_exclusion,
    plot_limit,
    plot_mc_stack,
    plot_ratio,
    poisson_errors,
    ratio_axes,
)
from .style import (
    STYLES,
    get_style_dict,
    reset_style,
    set_font,
    style_context,
    use_faser_style,
)

_RESOURCE_STACK = ExitStack()
atexit.register(_RESOURCE_STACK.close)


def _register_stylesheets() -> None:
    """Register the package directory with Matplotlib's style library idempotently."""
    style_dir = _RESOURCE_STACK.enter_context(
        resources.as_file(resources.files("faser_mpl_style"))
    )
    style_dir_str = str(style_dir)
    if hasattr(mpl_style, "USER_LIBRARY_PATHS"):
        user_paths: list[str] = mpl_style.USER_LIBRARY_PATHS
    else:
        from matplotlib.style import core as mpl_style_core

        user_paths = mpl_style_core.USER_LIBRARY_PATHS
    if style_dir_str not in user_paths:
        user_paths.append(style_dir_str)
    mpl_style.reload_library()


_register_stylesheets()
register_colors()
register_colormaps()

__all__ = [
    "__version__",
    "STYLES",
    "use_faser_style",
    "style_context",
    "set_font",
    "reset_style",
    "get_style_dict",
    "STATUS_ALIASES",
    "draw_faser_label",
    "draw_faser_logo",
    "set_xlabel",
    "set_ylabel",
    "set_zlabel",
    "draw_tag",
    "expand_ylim",
    "FASER_COLORS",
    "FASER_PALETTES",
    "get_palette",
    "set_color_cycle",
    "register_colors",
    "register_colormaps",
    "ratio_axes",
    "poisson_errors",
    "plot_1d",
    "plot_data",
    "plot_mc_stack",
    "plot_band",
    "plot_ratio",
    "plot_limit",
    "plot_exclusion",
    "plot_2d",
]
