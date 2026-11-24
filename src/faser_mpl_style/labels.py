"""FASER Collaboration branding stamps, transparent logo compositing, and axis label helpers."""

from __future__ import annotations

from collections.abc import Sequence
from importlib import resources
from typing import TYPE_CHECKING, Any, Literal

import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, HPacker, OffsetBox, OffsetImage, TextArea, VPacker

if TYPE_CHECKING:
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.colorbar import Colorbar
    from matplotlib.text import Text


def _root_figure(ax: Axes) -> Figure:
    """Return the root :class:`~matplotlib.figure.Figure` owning ``ax`` (handles ``SubFigure``)."""
    fig = ax.figure
    while not isinstance(fig, Figure):
        fig = fig.figure
    return fig

STATUS_ALIASES: dict[str, str] = {
    "": "",
    "final": "",
    "published": "",
    "prelim": "Preliminary",
    "preliminary": "Preliminary",
    "int": "Internal",
    "internal": "Internal",
    "sim": "Simulation",
    "simulation": "Simulation",
    "sim_prelim": "Simulation Preliminary",
    "sim-prelim": "Simulation Preliminary",
    "simulation preliminary": "Simulation Preliminary",
    "sim_int": "Simulation Internal",
    "sim-int": "Simulation Internal",
    "simulation internal": "Simulation Internal",
    "wip": "Work in Progress",
    "work in progress": "Work in Progress",
    "testbeam": "Testbeam",
    "test beam": "Test Beam",
}

_VALID_LOCS: tuple[str, ...] = (
    "upper left",
    "upper right",
    "lower left",
    "lower right",
    "outside",
)

_LOGO_CACHE: np.ndarray | None = None


def _load_logo_rgba() -> np.ndarray:
    """Load and cache the bundled transparent RGBA FASER logo as an immutable uint8 array."""
    global _LOGO_CACHE
    if _LOGO_CACHE is None:
        logo_ref = resources.files("faser_mpl_style.assets").joinpath("faser_logo.png")
        with resources.as_file(logo_ref) as logo_path:
            raw = np.asarray(mpimg.imread(str(logo_path)))
        if raw.dtype != np.uint8:
            arr = np.clip(np.round(raw * 255.0), 0.0, 255.0).astype(np.uint8)
        else:
            arr = raw.copy()
        arr.setflags(write=False)
        _LOGO_CACHE = arr
    return _LOGO_CACHE


def _resolve_status(status: str | None, simulation: bool) -> str:
    """Normalize a status string via :data:`STATUS_ALIASES` and optional ``simulation`` flag."""
    if status is None:
        resolved = ""
    else:
        key = status.strip().lower()
        resolved = STATUS_ALIASES[key] if key in STATUS_ALIASES else status.strip()

    if simulation and "simulation" not in resolved.lower():
        resolved = f"Simulation {resolved}".strip() if resolved else "Simulation"
    return resolved


def _format_com_lumi(
    com: float | str | None,
    lumi: float | str | None,
    lumi_unit: str,
    lumi_prefix: str,
) -> str:
    """Format center-of-mass energy and integrated luminosity text."""
    parts: list[str] = []

    if com is not None:
        if isinstance(com, str):
            text = com.strip()
            if "ev" in text.lower():
                if "=" in text or "$" in text or "\\sqrt" in text or "√" in text:
                    parts.append(text)
                else:
                    parts.append(rf"$\sqrt{{s}} =$ {text}")
            else:
                parts.append(rf"$\sqrt{{s}} = {text}\ \mathrm{{TeV}}$")
        else:
            parts.append(rf"$\sqrt{{s}} = {com:g}\ \mathrm{{TeV}}$")

    if lumi is not None:
        if isinstance(lumi, str):
            parts.append(lumi)
        else:
            val_str = f"{lumi:g}"
            unit_tex = rf"\mathrm{{{lumi_unit}}}^{{-1}}"
            if lumi_prefix == "":
                parts.append(rf"${val_str}\ {unit_tex}$")
            elif lumi_prefix == "calL":
                parts.append(rf"$\mathcal{{L}} = {val_str}\ {unit_tex}$")
            else:
                parts.append(rf"${lumi_prefix} = {val_str}\ {unit_tex}$")

    return ", ".join(parts)


def _format_experiment_header(experiment: str, status_str: str, usetex: bool) -> str:
    """Format the bold-italic experiment name and regular status suffix."""
    if experiment in ("FASERv", "FASERν"):
        if usetex:
            exp_part = r"\textbf{\textit{FASER}}\ensuremath{\nu}"
        else:
            exp_part = r"$\mathbfit{FASER}\nu$"
    else:
        escaped = experiment.replace(" ", r"\ ")
        if usetex:
            exp_part = rf"\textbf{{\textit{{{experiment}}}}}"
        else:
            exp_part = rf"$\mathbfit{{{escaped}}}$"

    if status_str:
        return f"{exp_part} {status_str}"
    return exp_part


def _normalize_desc(desc: str | Sequence[str] | None) -> list[str]:
    if desc is None:
        return []
    if isinstance(desc, str):
        return [desc] if desc else []
    return [str(line) for line in desc if str(line)]


def _apply_pad_y(
    ax: Axes,
    pad_y: bool | float,
    loc: str,
) -> None:
    if not pad_y:
        return
    fraction = 0.25 if isinstance(pad_y, bool) else float(pad_y)
    if fraction <= 0.0:
        return
    is_lower = loc in ("lower left", "lower right")
    expand_ylim(ax, fraction=fraction, top=not is_lower, bottom=is_lower)


def expand_ylim(
    ax: Axes | None = None,
    fraction: float = 0.25,
    *,
    top: bool = True,
    bottom: bool = False,
) -> tuple[float, float]:
    """Expand y-axis limits by ``fraction`` of the visible range (linear or log scale).

    Returns the new ``(ymin, ymax)`` tuple.
    """
    target_ax = ax if ax is not None else plt.gca()
    ymin, ymax = target_ax.get_ylim()

    if target_ax.get_yscale() == "log" and ymin > 0.0 and ymax > 0.0:
        log_lo = float(np.log10(ymin))
        log_hi = float(np.log10(ymax))
        span = log_hi - log_lo
        new_lo = float(10.0 ** (log_lo - fraction * span)) if bottom else float(ymin)
        new_hi = float(10.0 ** (log_hi + fraction * span)) if top else float(ymax)
    else:
        span = float(ymax - ymin)
        new_lo = float(ymin - fraction * span) if bottom else float(ymin)
        new_hi = float(ymax + fraction * span) if top else float(ymax)

    target_ax.set_ylim(new_lo, new_hi)
    return (new_lo, new_hi)


def draw_faser_logo(
    x: float | None = None,
    y: float | None = None,
    *,
    ax: Axes | None = None,
    width: float = 0.24,
    loc: Literal["upper left", "upper right", "lower left", "lower right", "outside"] = "upper left",
    status: str | None = None,
    simulation: bool = False,
    com: float | str | None = None,
    lumi: float | str | None = None,
    lumi_unit: str = "fb",
    lumi_prefix: str = "L",
    desc: str | Sequence[str] | None = None,
    layout: Literal["stacked", "inline"] = "stacked",
    color: str = "black",
    alpha: float = 1.0,
    fontsize: float | None = None,
    pad_y: bool | float = False,
    zorder: float = 10.0,
) -> list[Artist]:
    """Draw the official transparent RGBA FASER swooshed logo onto ``ax`` with DPI-invariant sizing.

    Returns the list of created Matplotlib :class:`~matplotlib.artist.Artist` objects.
    """
    if loc not in _VALID_LOCS:
        raise ValueError(f"Unknown loc {loc!r}; expected one of {_VALID_LOCS}.")
    if layout not in ("stacked", "inline"):
        raise ValueError(f"Unknown layout {layout!r}; expected 'stacked' or 'inline'.")
    if width <= 0.0:
        raise ValueError(f"width must be positive, got {width}.")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError(f"alpha must be in [0, 1], got {alpha}.")

    target_ax = ax if ax is not None else plt.gca()
    fig = _root_figure(target_ax)

    base_rgba = _load_logo_rgba()
    recolored = base_rgba.copy()
    rgb = np.round(np.asarray(mcolors.to_rgb(color), dtype=np.float64) * 255.0).astype(np.uint8)
    recolored[..., :3] = rgb
    if alpha < 1.0:
        scaled_alpha = np.round(recolored[..., 3].astype(np.float64) * float(alpha))
        recolored[..., 3] = np.clip(scaled_alpha, 0.0, 255.0).astype(np.uint8)

    bbox = target_ax.get_position()
    ax_w_in = float(fig.get_figwidth()) * float(bbox.width)
    zoom = (ax_w_in * float(width) * 72.0) / float(recolored.shape[1])
    img_box = OffsetImage(recolored, zoom=zoom, dpi_cor=True)

    status_str = _resolve_status(status, simulation)
    com_lumi_str = _format_com_lumi(com, lumi, lumi_unit, lumi_prefix)
    desc_lines = _normalize_desc(desc)

    base_fs = float(fontsize) if fontsize is not None else float(mpl.rcParams["font.size"]) * 0.95
    sub_fs = base_fs * 0.92

    artists: list[Artist] = []

    if loc == "outside":
        tx = 0.0 if x is None else float(x)
        ty = 1.025 if y is None else float(y)

        if status_str:
            status_area = TextArea(
                status_str,
                textprops={"fontsize": base_fs, "fontweight": "bold", "color": color, "alpha": alpha},
            )
            outside_box: OffsetBox = HPacker(
                children=[img_box, status_area], align="bottom", pad=0.0, sep=6.0
            )
        else:
            outside_box = img_box

        ab = AnnotationBbox(
            outside_box,
            (tx, ty),
            xycoords="axes fraction",
            box_alignment=(0.0, 0.0),
            frameon=False,
            pad=0.0,
            zorder=zorder,
        )
        target_ax.add_artist(ab)
        artists.append(ab)

        if com_lumi_str:
            txt_cl = target_ax.text(
                1.0,
                1.025 if y is None else float(y),
                com_lumi_str,
                transform=target_ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=base_fs,
                color=color,
                alpha=alpha,
                zorder=zorder,
            )
            artists.append(txt_cl)

        if desc_lines:
            txt_desc = target_ax.text(
                0.05,
                0.95,
                "\n".join(desc_lines),
                transform=target_ax.transAxes,
                ha="left",
                va="top",
                fontsize=sub_fs,
                color=color,
                alpha=alpha,
                zorder=zorder,
            )
            artists.append(txt_desc)
    else:
        loc_map: dict[
            str, tuple[float, float, tuple[float, float], Literal["left", "right"]]
        ] = {
            "upper left": (0.04, 0.96, (0.0, 1.0), "left"),
            "upper right": (0.96, 0.96, (1.0, 1.0), "right"),
            "lower left": (0.04, 0.04, (0.0, 0.0), "left"),
            "lower right": (0.96, 0.04, (1.0, 0.0), "right"),
        }
        def_x, def_y, box_align, pack_align = loc_map[loc]
        tx = def_x if x is None else float(x)
        ty = def_y if y is None else float(y)

        if layout == "stacked":
            children: list[Artist] = [img_box]
            if status_str:
                children.append(
                    TextArea(
                        status_str,
                        textprops={
                            "fontsize": base_fs,
                            "fontweight": "bold",
                            "color": color,
                            "alpha": alpha,
                        },
                    )
                )
            if com_lumi_str:
                children.append(
                    TextArea(
                        com_lumi_str,
                        textprops={"fontsize": sub_fs, "color": color, "alpha": alpha},
                    )
                )
            for line in desc_lines:
                children.append(
                    TextArea(
                        line,
                        textprops={"fontsize": sub_fs, "color": color, "alpha": alpha},
                    )
                )
            packed_box: OffsetBox = (
                VPacker(children=children, align=pack_align, pad=0.0, sep=3.0)
                if len(children) > 1
                else img_box
            )
        else:
            remaining_cl = com_lumi_str
            if status_str:
                top_row: OffsetBox = HPacker(
                    children=[
                        img_box,
                        TextArea(
                            status_str,
                            textprops={
                                "fontsize": base_fs,
                                "fontweight": "bold",
                                "color": color,
                                "alpha": alpha,
                            },
                        ),
                    ],
                    align="center",
                    pad=0.0,
                    sep=6.0,
                )
            elif remaining_cl and not desc_lines:
                top_row = HPacker(
                    children=[
                        img_box,
                        TextArea(
                            remaining_cl,
                            textprops={"fontsize": sub_fs, "color": color, "alpha": alpha},
                        ),
                    ],
                    align="center",
                    pad=0.0,
                    sep=6.0,
                )
                remaining_cl = ""
            else:
                top_row = img_box

            v_children: list[Artist] = [top_row]
            if remaining_cl:
                v_children.append(
                    TextArea(
                        remaining_cl,
                        textprops={"fontsize": sub_fs, "color": color, "alpha": alpha},
                    )
                )
            for line in desc_lines:
                v_children.append(
                    TextArea(
                        line,
                        textprops={"fontsize": sub_fs, "color": color, "alpha": alpha},
                    )
                )
            packed_box = (
                VPacker(children=v_children, align=pack_align, pad=0.0, sep=3.0)
                if len(v_children) > 1
                else top_row
            )

        ab = AnnotationBbox(
            packed_box,
            (tx, ty),
            xycoords="axes fraction",
            box_alignment=box_align,
            frameon=False,
            pad=0.0,
            zorder=zorder,
        )
        target_ax.add_artist(ab)
        artists.append(ab)

    _apply_pad_y(target_ax, pad_y, loc)
    return artists


def draw_faser_label(
    x: float | None = None,
    y: float | None = None,
    *,
    ax: Axes | None = None,
    experiment: str = "FASER",
    status: str | None = None,
    simulation: bool = False,
    com: float | str | None = None,
    lumi: float | str | None = None,
    lumi_unit: str = "fb",
    lumi_prefix: str = "L",
    desc: str | Sequence[str] | None = None,
    loc: Literal["upper left", "upper right", "lower left", "lower right", "outside"] = "upper left",
    style: Literal["text", "logo"] = "text",
    logo_width: float = 0.24,
    logo_color: str = "black",
    logo_layout: Literal["stacked", "inline"] = "stacked",
    fontsize: float | None = None,
    color: str = "black",
    pad_y: bool | float = False,
    **kwargs: Any,
) -> list[Artist]:
    """Draw a FASER collaboration experiment stamp (typographic or graphical logo).

    Returns the list of created Matplotlib :class:`~matplotlib.artist.Artist` objects.
    """
    if loc not in _VALID_LOCS:
        raise ValueError(f"Unknown loc {loc!r}; expected one of {_VALID_LOCS}.")

    target_ax = ax if ax is not None else plt.gca()

    if style == "logo":
        logo_kwargs: dict[str, Any] = {}
        if "alpha" in kwargs:
            logo_kwargs["alpha"] = kwargs["alpha"]
        if "zorder" in kwargs:
            logo_kwargs["zorder"] = kwargs["zorder"]
        return draw_faser_logo(
            x=x,
            y=y,
            ax=target_ax,
            width=logo_width,
            loc=loc,
            status=status,
            simulation=simulation,
            com=com,
            lumi=lumi,
            lumi_unit=lumi_unit,
            lumi_prefix=lumi_prefix,
            desc=desc,
            layout=logo_layout,
            color=logo_color,
            fontsize=fontsize,
            pad_y=pad_y,
            **logo_kwargs,
        )

    if style != "text":
        raise ValueError(f"Unknown style {style!r}; expected 'text' or 'logo'.")

    status_str = _resolve_status(status, simulation)
    com_lumi_str = _format_com_lumi(com, lumi, lumi_unit, lumi_prefix)
    desc_lines = _normalize_desc(desc)
    usetex = bool(mpl.rcParams.get("text.usetex", False))

    header_str = _format_experiment_header(experiment, status_str, usetex)
    base_fs = float(fontsize) if fontsize is not None else float(mpl.rcParams["font.size"]) * 1.15
    sub_fs = base_fs * 0.85

    text_kwargs = dict(kwargs)
    text_kwargs.setdefault("zorder", 10.0)

    artists: list[Artist] = []

    if loc == "outside":
        tx = 0.0 if x is None else float(x)
        ty = 1.02 if y is None else float(y)
        hdr = target_ax.text(
            tx,
            ty,
            header_str,
            transform=target_ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=base_fs,
            color=color,
            **text_kwargs,
        )
        artists.append(hdr)

        if com_lumi_str:
            cl_txt = target_ax.text(
                1.0,
                ty,
                com_lumi_str,
                transform=target_ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=sub_fs,
                color=color,
                **text_kwargs,
            )
            artists.append(cl_txt)

        if desc_lines:
            desc_txt = target_ax.text(
                0.05,
                0.95,
                "\n".join(desc_lines),
                transform=target_ax.transAxes,
                ha="left",
                va="top",
                fontsize=sub_fs,
                color=color,
                linespacing=1.25,
                **text_kwargs,
            )
            artists.append(desc_txt)
    else:
        loc_defaults: dict[str, tuple[float, float, str, str]] = {
            "upper left": (0.05, 0.95, "left", "top"),
            "upper right": (0.95, 0.95, "right", "top"),
            "lower left": (0.05, 0.05, "left", "bottom"),
            "lower right": (0.95, 0.05, "right", "bottom"),
        }
        def_x, def_y, ha, va = loc_defaults[loc]
        tx = def_x if x is None else float(x)
        ty = def_y if y is None else float(y)

        sub_lines = ([com_lumi_str] if com_lumi_str else []) + desc_lines
        fig = _root_figure(target_ax)
        ax_h_pts = max(float(fig.get_figheight()) * float(target_ax.get_position().height) * 72.0, 1.0)

        if va == "top":
            hdr = target_ax.text(
                tx,
                ty,
                header_str,
                transform=target_ax.transAxes,
                ha=ha,
                va="top",
                fontsize=base_fs,
                color=color,
                **text_kwargs,
            )
            artists.append(hdr)
            if sub_lines:
                dy = (1.38 * base_fs) / ax_h_pts
                sub = target_ax.text(
                    tx,
                    ty - dy,
                    "\n".join(sub_lines),
                    transform=target_ax.transAxes,
                    ha=ha,
                    va="top",
                    fontsize=sub_fs,
                    color=color,
                    linespacing=1.28,
                    **text_kwargs,
                )
                artists.append(sub)
        else:
            if sub_lines:
                sub = target_ax.text(
                    tx,
                    ty,
                    "\n".join(sub_lines),
                    transform=target_ax.transAxes,
                    ha=ha,
                    va="bottom",
                    fontsize=sub_fs,
                    color=color,
                    linespacing=1.28,
                    **text_kwargs,
                )
                sub_h = (len(sub_lines) * 1.28 * sub_fs + 0.35 * base_fs) / ax_h_pts
                hdr = target_ax.text(
                    tx,
                    ty + sub_h,
                    header_str,
                    transform=target_ax.transAxes,
                    ha=ha,
                    va="bottom",
                    fontsize=base_fs,
                    color=color,
                    **text_kwargs,
                )
                artists.extend([hdr, sub])
            else:
                hdr = target_ax.text(
                    tx,
                    ty,
                    header_str,
                    transform=target_ax.transAxes,
                    ha=ha,
                    va="bottom",
                    fontsize=base_fs,
                    color=color,
                    **text_kwargs,
                )
                artists.append(hdr)

    _apply_pad_y(target_ax, pad_y, loc)
    return artists


def set_xlabel(label: str, ax: Axes | None = None, **kwargs: Any) -> Text:
    """Set right-aligned ATLAS/FASER x-axis label.

    If ``ax`` is the top main panel created by :func:`~faser_mpl_style.ratio_axes`,
    automatically forwards the label to the bottom-most linked ratio axes.
    """
    target_ax = ax if ax is not None else plt.gca()
    linked = getattr(target_ax, "_faser_linked_axes", None)
    if linked and len(linked) > 1 and target_ax is linked[0]:
        target_ax = linked[-1]

    if "loc" not in kwargs and "ha" not in kwargs and "horizontalalignment" not in kwargs:
        kwargs["loc"] = "right"
    return target_ax.set_xlabel(label, **kwargs)


def set_ylabel(label: str, ax: Axes | None = None, **kwargs: Any) -> Text:
    """Set top-aligned ATLAS/FASER y-axis label and align linked ratio panel y-labels."""
    target_ax = ax if ax is not None else plt.gca()
    if "loc" not in kwargs and "va" not in kwargs and "verticalalignment" not in kwargs:
        kwargs["loc"] = "top"
    txt = target_ax.set_ylabel(label, **kwargs)

    linked = getattr(target_ax, "_faser_linked_axes", None)
    if linked and target_ax.figure is not None:
        target_ax.figure.align_ylabels(list(linked))
    return txt


def set_zlabel(label: str, cbar: Colorbar, **kwargs: Any) -> Text:
    """Set top-aligned colorbar axis label."""
    if "loc" not in kwargs and "va" not in kwargs and "verticalalignment" not in kwargs:
        kwargs["loc"] = "top" if cbar.orientation == "vertical" else "right"
    cbar.set_label(label, **kwargs)
    if cbar.orientation == "horizontal":
        return cbar.ax.xaxis.label
    return cbar.ax.yaxis.label


def draw_tag(
    text: str,
    ax: Axes | None = None,
    *,
    fontsize: float | None = None,
    **kwargs: Any,
) -> Text:
    """Draw a small right-aligned metadata/version tag above the top-right corner of ``ax``."""
    target_ax = ax if ax is not None else plt.gca()
    fs = float(fontsize) if fontsize is not None else max(float(mpl.rcParams["font.size"]) * 0.72, 8.0)
    tag_kwargs = dict(kwargs)
    tag_kwargs.setdefault("ha", "right")
    tag_kwargs.setdefault("va", "bottom")
    tag_kwargs.setdefault("color", "faser:gray")
    tag_kwargs.setdefault("transform", target_ax.transAxes)
    return target_ax.text(1.0, 1.015, text, fontsize=fs, **tag_kwargs)
