"""High-level HEP plotting helpers tailored to FASER Collaboration figures."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .colors import get_palette
from .labels import set_ylabel, set_zlabel

if TYPE_CHECKING:
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.collections import PolyCollection, QuadMesh
    from matplotlib.colorbar import Colorbar
    from matplotlib.container import ErrorbarContainer
    from matplotlib.figure import Figure
    from matplotlib.patches import StepPatch
    from numpy.typing import ArrayLike

# Exact 1-sigma (alpha = 1 - erf(1/sqrt(2)) = 0.31731050786291415) Garwood
# lower and upper Poisson errors for integer counts N = 0..50.
_GARWOOD_ALPHA_1SIGMA: float = 0.31731050786291415

_GARWOOD_1SIGMA_LOW: tuple[float, ...] = (
    0.0,
    0.827246220977,
    1.291814560181,
    1.63270468611,
    1.914339186223,
    2.159691144407,
    2.379931379296,
    2.581470456066,
    2.768386056463,
    2.943461037251,
    3.108694439362,
    3.265579400951,
    3.4152659943,
    3.558662330438,
    3.696500318824,
    3.829380098575,
    3.957801029404,
    4.082183899342,
    4.20288721196,
    4.320219374655,
    4.434447982214,
    4.545806999323,
    4.654502395445,
    4.760716621072,
    4.864612203845,
    4.96633466721,
    5.066014921356,
    5.163771238556,
    5.259710897935,
    5.353931564852,
    5.446522455436,
    5.537565325806,
    5.627135317186,
    5.715301681784,
    5.802128409355,
    5.887674770585,
    5.971995790393,
    6.055142661895,
    6.137163109883,
    6.218101711133,
    6.298000177664,
    6.376897608042,
    6.454830711028,
    6.531834005214,
    6.607939997708,
    6.683179344507,
    6.757580994791,
    6.831172321077,
    6.903979236874,
    6.976026303297,
    7.047336825856,
)

_GARWOOD_1SIGMA_HIGH: tuple[float, ...] = (
    1.841021645009,
    2.299526559116,
    2.637859623455,
    2.918185832883,
    3.162753172261,
    3.382472652147,
    3.583641545985,
    3.770280720434,
    3.945141519869,
    4.110204137668,
    4.266949761009,
    4.416520523166,
    4.559819057391,
    4.697573372609,
    4.830380755688,
    4.958738432721,
    5.083065564016,
    5.203719389884,
    5.321007322384,
    5.435196161482,
    5.546519229511,
    5.655181971183,
    5.761366404113,
    5.86523469569,
    5.966932067114,
    6.06658917312,
    6.164324068605,
    6.260243846553,
    6.354446012006,
    6.447019642275,
    6.538046372668,
    6.627601238785,
    6.715753400076,
    6.802566764512,
    6.888100530385,
    6.972409658304,
    7.055545284061,
    7.137555081187,
    7.21848358048,
    7.298372452597,
    7.377260758797,
    7.455185174101,
    7.532180186515,
    7.608278275353,
    7.683510071295,
    7.75790450042,
    7.831488914112,
    7.904289206521,
    7.976329920983,
    8.047634346662,
    8.118224606473,
)


def _norm_ppf(p: float) -> float:
    """High-precision Acklam rational approximation for standard normal inverse CDF."""
    if not (0.0 < p < 1.0):
        raise ValueError(f"Probability p must be in (0, 1), got {p}.")

    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )

    p_low = 0.02425
    p_high = 1.0 - p_low
    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (
            (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        ) / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
        (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
    )


def _gammainc_lower_reg(a: float, x: float) -> float:
    """Regularized lower incomplete gamma function P(a, x)."""
    if x <= 0.0:
        return 0.0
    if x < a + 1.0:
        ap = a
        term = 1.0 / a
        total = term
        for _ in range(500):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))

    b = x + 1.0 - a
    c = 1.0 / 1e-30
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return 1.0 - q


def _chi2_half_ppf(p: float, a: float) -> float:
    """Compute ``0.5 * chi2.ppf(p, df=2*a)``, i.e. inverse of regularized gamma ``P(a, x) = p``."""
    if a == 1.0:
        return -math.log(1.0 - p)
    df = 2.0 * a
    z = _norm_ppf(p)
    term = 1.0 - 2.0 / (9.0 * df) + z * math.sqrt(2.0 / (9.0 * df))
    x = max(0.5 * df * (term**3) if term > 0.0 else 1e-6, 1e-12)

    # 3 safeguarded Newton steps refine Wilson-Hilferty to ~1e-12 relative accuracy
    lgamma_a = math.lgamma(a)
    for _ in range(4):
        err = _gammainc_lower_reg(a, x) - p
        if abs(err) < 1e-12:
            break
        log_pdf = (a - 1.0) * math.log(x) - x - lgamma_a
        if log_pdf < -700.0:
            break
        pdf = math.exp(log_pdf)
        step = err / pdf
        x_new = x - step
        x = x_new if x_new > 0.0 else 0.5 * x
    return x


def ratio_axes(
    figsize: tuple[float, float] | None = None,
    *,
    height_ratios: Sequence[float] | None = None,
    hspace: float = 0.06,
    extra_axes: int = 0,
    sharex: bool = True,
) -> tuple[Figure, Axes, Axes] | tuple[Figure, Axes, list[Axes]]:
    """Create a publication-ready main + ratio figure (or main + multiple ratio panels).

    Returns ``(fig, main_ax, ratio_ax)`` when ``extra_axes == 0`` or
    ``(fig, main_ax, [ratio_ax_1, ...])`` when ``extra_axes >= 1``.
    """
    if extra_axes < 0:
        raise ValueError(f"extra_axes must be non-negative, got {extra_axes}.")

    n_ratio = 1 + extra_axes
    n_total = 1 + n_ratio

    if height_ratios is None:
        ratios = [3.0] + [1.0] * n_ratio
    else:
        ratios = [float(r) for r in height_ratios]
        if len(ratios) != n_total:
            raise ValueError(
                f"height_ratios must have length {n_total}, got {len(ratios)}."
            )

    if figsize is None:
        rc_w, rc_h = mpl.rcParams["figure.figsize"]
        figsize = (float(rc_w), float(rc_h) * (1.0 + 0.28 * n_ratio))

    fig, axes = plt.subplots(
        n_total,
        1,
        figsize=figsize,
        sharex=sharex,
        gridspec_kw={"height_ratios": ratios, "hspace": hspace},
    )
    axes_list: list[Axes] = list(np.ravel(axes))
    main_ax = axes_list[0]
    ratio_list = axes_list[1:]

    for upper_ax in axes_list[:-1]:
        upper_ax.tick_params(labelbottom=False)

    if hspace == 0.0:
        for rax in ratio_list:
            rax.yaxis.set_major_locator(MaxNLocator(nbins=5, prune="upper"))

    linked = tuple(axes_list)
    for panel in axes_list:
        panel._faser_linked_axes = linked  # type: ignore[attr-defined]

    if extra_axes == 0:
        return (fig, main_ax, ratio_list[0])
    return (fig, main_ax, ratio_list)


def poisson_errors(
    counts: ArrayLike,
    *,
    method: Literal["garwood", "sqrt"] = "garwood",
    alpha: float = _GARWOOD_ALPHA_1SIGMA,
) -> np.ndarray:
    """Compute asymmetric ``(2, N)`` ``[lower, upper]`` statistical errors for Poisson bin counts.

    Uses exact 1-sigma Garwood chi-squared intervals (scipy-free via exact
    lookup table for integer ``N <= 50`` and Wilson-Hilferty + Newton
    refinement for ``N > 50`` or custom ``alpha``).
    """
    c = np.asarray(counts, dtype=np.float64)
    if c.ndim == 0:
        c = c.reshape(1)
    if c.ndim != 1:
        raise ValueError(f"counts must be 1D, got shape {c.shape}.")
    if np.any(c < 0.0):
        raise ValueError("counts must be non-negative.")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1), got {alpha}.")

    if c.size == 0:
        return np.zeros((2, 0), dtype=np.float64)

    if method == "sqrt":
        err = np.sqrt(c)
        return np.vstack([err, err])

    if method != "garwood":
        raise ValueError(f"Unknown method {method!r}; expected 'garwood' or 'sqrt'.")

    try:
        from scipy.stats import chi2
    except ImportError:
        chi2 = None

    if chi2 is not None:
        safe_pos = np.where(c > 0.0, c, 1.0)
        lower = np.where(c > 0.0, c - 0.5 * chi2.ppf(alpha / 2.0, 2.0 * safe_pos), 0.0)
        upper = 0.5 * chi2.ppf(1.0 - alpha / 2.0, 2.0 * (c + 1.0)) - c
        return np.vstack([np.asarray(lower, dtype=np.float64), np.asarray(upper, dtype=np.float64)])

    use_table = abs(alpha - _GARWOOD_ALPHA_1SIGMA) < 1e-9
    lower_out = np.empty(c.size, dtype=np.float64)
    upper_out = np.empty(c.size, dtype=np.float64)
    p_lo = alpha / 2.0
    p_hi = 1.0 - alpha / 2.0

    for idx, val in enumerate(c):
        n_int = int(round(float(val)))
        if use_table and 0 <= n_int <= 50 and abs(float(val) - n_int) < 1e-12:
            lower_out[idx] = _GARWOOD_1SIGMA_LOW[n_int]
            upper_out[idx] = _GARWOOD_1SIGMA_HIGH[n_int]
        else:
            v = float(val)
            lower_out[idx] = 0.0 if v == 0.0 else v - _chi2_half_ppf(p_lo, v)
            upper_out[idx] = _chi2_half_ppf(p_hi, v + 1.0) - v

    return np.vstack([lower_out, upper_out])


def _to_asymmetric_err(err: ArrayLike, n: int) -> np.ndarray:
    """Normalize a 1D symmetric or ``(2, N)`` asymmetric error array to shape ``(2, N)``."""
    arr = np.asarray(err, dtype=np.float64)
    if arr.ndim == 1 and arr.shape[0] == n:
        return np.vstack([arr, arr])
    if arr.ndim == 2 and arr.shape == (2, n):
        return arr
    raise ValueError(f"Expected error array of shape ({n},) or (2, {n}), got {arr.shape}.")


def _resolve_bins(
    bins: ArrayLike,
    n: int,
) -> tuple[np.ndarray, np.ndarray | None, bool, np.ndarray]:
    """Return ``(centers, half_widths, is_edges, raw_bins)``."""
    b = np.asarray(bins, dtype=np.float64)
    if b.ndim != 1:
        raise ValueError(f"bins must be 1D, got shape {b.shape}.")
    if b.size == n + 1:
        centers = 0.5 * (b[:-1] + b[1:])
        half_widths = 0.5 * (b[1:] - b[:-1])
        return (centers, half_widths, True, b)
    if b.size == n:
        return (b, None, False, b)
    raise ValueError(
        f"len(bins) must equal len(values) + 1 (edges) or len(values) (centers); "
        f"got len(bins)={b.size} and len(values)={n}."
    )


def plot_band(
    x: ArrayLike,
    low: ArrayLike,
    high: ArrayLike,
    *,
    label: str | None = None,
    color: str | None = None,
    alpha: float = 0.30,
    hatch: str | None = None,
    edgecolor: str | None = None,
    linewidth: float = 0.0,
    ax: Axes | None = None,
    **kwargs: Any,
) -> PolyCollection:
    """Plot a shaded or hatched uncertainty band for continuous curves or binned step edges."""
    target_ax = ax if ax is not None else plt.gca()
    x_arr = np.asarray(x, dtype=np.float64)
    lo = np.asarray(low, dtype=np.float64)
    hi = np.asarray(high, dtype=np.float64)

    if lo.ndim != 1 or hi.ndim != 1 or lo.shape != hi.shape:
        raise ValueError(f"low and high must be 1D arrays of equal length, got {lo.shape} and {hi.shape}.")

    if x_arr.size == lo.size:
        xs, y1, y2 = x_arr, lo, hi
    elif x_arr.size == lo.size + 1:
        xs = np.repeat(x_arr, 2)[1:-1]
        y1 = np.repeat(lo, 2)
        y2 = np.repeat(hi, 2)
    else:
        raise ValueError(
            f"len(x) must equal len(low) or len(low) + 1; got len(x)={x_arr.size}, len(low)={lo.size}."
        )

    fb_kwargs = dict(kwargs)
    if hatch is not None:
        fb_kwargs.setdefault("facecolor", "none")
        ec = edgecolor if edgecolor is not None else (color if color is not None else "faser:unc-band")
        fb_kwargs["edgecolor"] = ec
        fb_kwargs["hatch"] = hatch
        fb_kwargs["linewidth"] = linewidth
        fb_kwargs["alpha"] = alpha
    else:
        if color is not None:
            fb_kwargs.setdefault("facecolor", color)
        if edgecolor is not None:
            fb_kwargs["edgecolor"] = edgecolor
        fb_kwargs["linewidth"] = linewidth
        fb_kwargs["alpha"] = alpha

    return target_ax.fill_between(xs, y1, y2, label=label, **fb_kwargs)


def plot_1d(
    bins: ArrayLike,
    values: ArrayLike,
    *,
    yerr: ArrayLike | None = None,
    label: str | None = None,
    color: str | None = None,
    linewidth: float | None = None,
    linestyle: str = "-",
    fill: bool = False,
    fill_alpha: float = 0.25,
    band: bool = False,
    band_alpha: float = 0.28,
    band_hatch: str | None = None,
    autolim: bool = True,
    ax: Axes | None = None,
    **kwargs: Any,
) -> StepPatch:
    """Plot a 1D binned step histogram with optional translucent fill and uncertainty band."""
    target_ax = ax if ax is not None else plt.gca()
    edges = np.asarray(bins, dtype=np.float64)
    vals = np.asarray(values, dtype=np.float64)
    if edges.ndim != 1 or vals.ndim != 1 or edges.size != vals.size + 1:
        raise ValueError(
            f"bins must be 1D with length len(values) + 1; got bins={edges.shape}, values={vals.shape}."
        )

    lw = float(linewidth) if linewidth is not None else float(mpl.rcParams["lines.linewidth"])
    stairs_kwargs = dict(kwargs)

    if fill:
        resolved_color = (
            color
            if color is not None
            else cast(str, target_ax._get_lines.get_next_color())  # type: ignore[attr-defined]
        )
        stairs_kwargs.setdefault("facecolor", mcolors.to_rgba(resolved_color, fill_alpha))
        stairs_kwargs.setdefault("edgecolor", resolved_color)
        patch = target_ax.stairs(
            vals,
            edges,
            fill=True,
            linewidth=lw,
            linestyle=linestyle,
            label=label,
            **stairs_kwargs,
        )
    else:
        if color is not None:
            stairs_kwargs["color"] = color
        patch = target_ax.stairs(
            vals,
            edges,
            fill=False,
            linewidth=lw,
            linestyle=linestyle,
            label=label,
            **stairs_kwargs,
        )

    if yerr is not None and (band or band_hatch is not None):
        err2d = _to_asymmetric_err(yerr, vals.size)
        band_col: Any = color if color is not None else patch.get_edgecolor()
        plot_band(
            edges,
            vals - err2d[0],
            vals + err2d[1],
            color=band_col,
            alpha=0.80 if band_hatch is not None else band_alpha,
            hatch=band_hatch,
            ax=target_ax,
        )

    if autolim:
        target_ax.set_xlim(float(edges[0]), float(edges[-1]))

    return patch


def plot_data(
    bins: ArrayLike,
    counts: ArrayLike,
    *,
    yerr: Literal["poisson", "sqrt"] | ArrayLike | None = "poisson",
    xerr: bool | ArrayLike = False,
    label: str = "Data",
    color: str = "faser:data",
    marker: str = "o",
    markersize: float = 6.0,
    elinewidth: float = 1.4,
    capsize: float | None = None,
    show_zero: bool = False,
    autolim: bool = True,
    ax: Axes | None = None,
    **kwargs: Any,
) -> ErrorbarContainer:
    """Plot binned experimental data points with Poisson or custom error bars."""
    target_ax = ax if ax is not None else plt.gca()
    c = np.asarray(counts, dtype=np.float64)
    if c.ndim != 1:
        raise ValueError(f"counts must be 1D, got shape {c.shape}.")

    centers, half_widths, is_edges, raw_bins = _resolve_bins(bins, c.size)

    yerr_arr: np.ndarray | None
    if isinstance(yerr, str):
        if yerr == "poisson":
            yerr_arr = poisson_errors(c, method="garwood")
        elif yerr == "sqrt":
            yerr_arr = poisson_errors(c, method="sqrt")
        else:
            raise ValueError(f"Unknown yerr mode {yerr!r}; expected 'poisson', 'sqrt', array, or None.")
    elif yerr is None:
        yerr_arr = None
    else:
        yerr_arr = np.asarray(yerr, dtype=np.float64)

    xerr_arr: np.ndarray | None
    if isinstance(xerr, bool):
        if xerr:
            if not is_edges or half_widths is None:
                raise ValueError("xerr=True requires bin edges (len(bins) == len(counts) + 1).")
            xerr_arr = half_widths
        else:
            xerr_arr = None
    else:
        xerr_arr = np.asarray(xerr, dtype=np.float64)

    mask = np.ones(c.size, dtype=bool) if show_zero else (c > 0.0)

    def _mask_err(arr: np.ndarray | None) -> np.ndarray | None:
        if arr is None:
            return None
        if arr.ndim == 2:
            return arr[:, mask]
        return arr[mask]

    eb_kwargs = dict(kwargs)
    eb_kwargs.setdefault("linestyle", "none")
    eb_kwargs.setdefault("zorder", 5)
    if capsize is not None:
        eb_kwargs["capsize"] = capsize

    container = target_ax.errorbar(
        centers[mask],
        c[mask],
        yerr=_mask_err(yerr_arr),
        xerr=_mask_err(xerr_arr),
        marker=marker,
        color=color,
        markersize=markersize,
        elinewidth=elinewidth,
        label=label,
        **eb_kwargs,
    )

    if autolim and is_edges:
        target_ax.set_xlim(float(raw_bins[0]), float(raw_bins[-1]))

    return container


def plot_mc_stack(
    bins: ArrayLike,
    hists: Sequence[ArrayLike],
    labels: Sequence[str],
    *,
    colors: Sequence[str] | None = None,
    yerr: Sequence[ArrayLike] | None = None,
    total_err: ArrayLike | None = None,
    err_label: str | None = r"Stat. $\oplus$ Syst.",
    err_style: Literal["hatch", "fill"] = "hatch",
    err_color: str = "faser:unc-band",
    edgecolor: str = "black",
    linewidth: float = 0.8,
    alpha: float = 0.9,
    autolim: bool = True,
    ax: Axes | None = None,
    **kwargs: Any,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Plot stacked filled MC background histograms with optional total uncertainty band.

    Returns ``(total, total_err)``.
    """
    if not hists:
        raise ValueError("hists must contain at least one histogram.")
    if len(hists) != len(labels):
        raise ValueError(f"len(hists) ({len(hists)}) must match len(labels) ({len(labels)}).")
    if err_style not in ("hatch", "fill"):
        raise ValueError(f"Unknown err_style {err_style!r}; expected 'hatch' or 'fill'.")

    target_ax = ax if ax is not None else plt.gca()
    edges = np.asarray(bins, dtype=np.float64)
    n_bins = edges.size - 1
    if edges.ndim != 1 or n_bins <= 0:
        raise ValueError("bins must be a 1D array of at least 2 bin edges.")

    arrays: list[np.ndarray] = []
    for idx, h in enumerate(hists):
        arr = np.asarray(h, dtype=np.float64)
        if arr.ndim != 1 or arr.size != n_bins:
            raise ValueError(f"Histogram {idx} has shape {arr.shape}, expected ({n_bins},).")
        arrays.append(arr)

    pal = list(colors) if colors is not None else get_palette("faser-stack", len(arrays))
    if len(pal) < len(arrays):
        raise ValueError(f"Provided {len(pal)} colors for {len(arrays)} histograms.")

    baseline = np.zeros(n_bins, dtype=np.float64)
    for arr, lbl, col in zip(arrays, labels, pal):
        top = baseline + arr
        target_ax.stairs(
            top,
            edges,
            baseline=baseline,
            fill=True,
            facecolor=mcolors.to_rgba(col, alpha),
            edgecolor=edgecolor,
            linewidth=linewidth,
            label=lbl,
            **kwargs,
        )
        baseline = top

    total = baseline.copy()
    tot_err_arr: np.ndarray | None = None

    if total_err is not None:
        tot_err_arr = np.asarray(total_err, dtype=np.float64)
    elif yerr is not None:
        if len(yerr) != len(arrays):
            raise ValueError(f"len(yerr) ({len(yerr)}) must match len(hists) ({len(arrays)}).")
        err_arrays = [np.asarray(e, dtype=np.float64) for e in yerr]
        if any(e.ndim == 2 for e in err_arrays):
            promoted = [_to_asymmetric_err(e, n_bins) for e in err_arrays]
            tot_err_arr = np.sqrt(np.sum([e**2 for e in promoted], axis=0))
        else:
            tot_err_arr = np.sqrt(np.sum([e**2 for e in err_arrays], axis=0))

    if tot_err_arr is not None:
        err2d = _to_asymmetric_err(tot_err_arr, n_bins)
        lo = total - err2d[0]
        hi = total + err2d[1]
        if err_style == "hatch":
            plot_band(
                edges,
                lo,
                hi,
                label=err_label,
                color=err_color,
                hatch="////",
                alpha=0.85,
                linewidth=0.0,
                ax=target_ax,
                zorder=4,
            )
        else:
            plot_band(
                edges,
                lo,
                hi,
                label=err_label,
                color=err_color,
                alpha=0.35,
                linewidth=0.0,
                ax=target_ax,
                zorder=4,
            )

    if autolim:
        target_ax.set_xlim(float(edges[0]), float(edges[-1]))

    return (total, tot_err_arr)


def plot_ratio(
    bins: ArrayLike,
    num: ArrayLike,
    den: ArrayLike,
    *,
    num_err: ArrayLike | None = None,
    den_err: ArrayLike | None = None,
    mode: Literal["ratio", "diff", "pull"] = "ratio",
    ref_line: float | None = None,
    ylim: tuple[float, float] | None = None,
    ylabel: str | None = None,
    color: str = "faser:data",
    marker: str = "o",
    markersize: float = 5.5,
    band_color: str = "faser:unc-band",
    band_style: Literal["hatch", "fill"] = "hatch",
    offscale_arrows: bool = True,
    xerr: bool = False,
    ax: Axes | None = None,
    **kwargs: Any,
) -> ErrorbarContainer:
    """Plot a Data/MC ratio, fractional difference, or pull panel."""
    if mode not in ("ratio", "diff", "pull"):
        raise ValueError(f"Unknown mode {mode!r}; expected 'ratio', 'diff', or 'pull'.")
    if band_style not in ("hatch", "fill"):
        raise ValueError(f"Unknown band_style {band_style!r}; expected 'hatch' or 'fill'.")

    target_ax = ax if ax is not None else plt.gca()
    num_arr = np.asarray(num, dtype=np.float64)
    den_arr = np.asarray(den, dtype=np.float64)
    if num_arr.ndim != 1 or den_arr.ndim != 1 or num_arr.shape != den_arr.shape:
        raise ValueError(
            f"num and den must be 1D arrays of equal length, got {num_arr.shape} and {den_arr.shape}."
        )

    n = num_arr.size
    centers, half_widths, is_edges, raw_bins = _resolve_bins(bins, n)

    if mode == "ratio":
        ref = 1.0 if ref_line is None else float(ref_line)
        yl = (0.5, 1.5) if ylim is None else ylim
        ylbl = "Data / MC" if ylabel is None else ylabel
    elif mode == "diff":
        ref = 0.0 if ref_line is None else float(ref_line)
        yl = (-0.5, 0.5) if ylim is None else ylim
        ylbl = "(Data - MC) / MC" if ylabel is None else ylabel
    else:
        ref = 0.0 if ref_line is None else float(ref_line)
        yl = (-3.5, 3.5) if ylim is None else ylim
        ylbl = "Pull" if ylabel is None else ylabel

    target_ax.axhline(
        ref,
        color="black",
        linestyle="-" if mode == "pull" else "--",
        linewidth=0.9,
        zorder=1,
    )
    if mode == "pull":
        for level in (-1.0, 1.0):
            target_ax.axhline(level, color="#888888", linestyle="--", linewidth=0.7, alpha=0.8, zorder=1)
        for level in (-2.0, 2.0):
            target_ax.axhline(level, color="#AAAAAA", linestyle=":", linewidth=0.7, alpha=0.8, zorder=1)

    num_err_2d = _to_asymmetric_err(num_err, n) if num_err is not None else None
    den_err_2d = _to_asymmetric_err(den_err, n) if den_err is not None else None

    yerr_plot: np.ndarray | None = None

    with np.errstate(divide="ignore", invalid="ignore"):
        if mode in ("ratio", "diff"):
            valid = den_arr != 0.0
            safe_den = np.where(valid, den_arr, 1.0)
            y = (
                np.where(valid, num_arr / safe_den, np.nan)
                if mode == "ratio"
                else np.where(valid, (num_arr - den_arr) / safe_den, np.nan)
            )
            if num_err_2d is not None:
                yerr_plot = np.where(valid, num_err_2d / np.abs(safe_den), 0.0)

            if den_err_2d is not None:
                rel_lo = np.where(valid, den_err_2d[0] / np.abs(safe_den), 0.0)
                rel_hi = np.where(valid, den_err_2d[1] / np.abs(safe_den), 0.0)
                if band_style == "hatch":
                    plot_band(
                        raw_bins,
                        ref - rel_lo,
                        ref + rel_hi,
                        color=band_color,
                        hatch="////",
                        alpha=0.85,
                        linewidth=0.0,
                        ax=target_ax,
                        zorder=2,
                    )
                else:
                    plot_band(
                        raw_bins,
                        ref - rel_lo,
                        ref + rel_hi,
                        color=band_color,
                        alpha=0.35,
                        linewidth=0.0,
                        ax=target_ax,
                        zorder=2,
                    )
        else:
            diff = num_arr - den_arr
            if num_err_2d is not None:
                sig_num = np.where(diff >= 0.0, num_err_2d[0], num_err_2d[1])
            elif den_err_2d is None:
                sig_num = np.sqrt(np.maximum(den_arr, 0.0))
            else:
                sig_num = np.zeros(n, dtype=np.float64)

            if den_err_2d is not None:
                sig_den = np.where(diff >= 0.0, den_err_2d[1], den_err_2d[0])
            else:
                sig_den = np.zeros(n, dtype=np.float64)

            sigma = np.sqrt(sig_num**2 + sig_den**2)
            valid = sigma > 0.0
            safe_sigma = np.where(valid, sigma, 1.0)
            y = np.where(valid, diff / safe_sigma, np.nan)

    xerr_valid: np.ndarray | None = None
    if xerr:
        if not is_edges or half_widths is None:
            raise ValueError("xerr=True requires bin edges (len(bins) == len(num) + 1).")
        xerr_valid = half_widths[valid]

    yerr_valid = yerr_plot[:, valid] if yerr_plot is not None else None

    eb_kwargs = dict(kwargs)
    eb_kwargs.setdefault("linestyle", "none")
    eb_kwargs.setdefault("elinewidth", 1.2)
    eb_kwargs.setdefault("zorder", 5)

    container = target_ax.errorbar(
        centers[valid],
        y[valid],
        yerr=yerr_valid,
        xerr=xerr_valid,
        marker=marker,
        color=color,
        markersize=markersize,
        **eb_kwargs,
    )

    y_lo_lim, y_hi_lim = float(yl[0]), float(yl[1])
    if offscale_arrows and np.any(valid):
        span = y_hi_lim - y_lo_lim
        above = valid & (y > y_hi_lim)
        below = valid & (y < y_lo_lim)
        if np.any(above):
            target_ax.plot(
                centers[above],
                np.full(int(np.sum(above)), y_hi_lim - 0.045 * span),
                marker="^",
                linestyle="none",
                color="faser:red",
                markersize=markersize + 1.0,
                zorder=6,
            )
        if np.any(below):
            target_ax.plot(
                centers[below],
                np.full(int(np.sum(below)), y_lo_lim + 0.045 * span),
                marker="v",
                linestyle="none",
                color="faser:red",
                markersize=markersize + 1.0,
                zorder=6,
            )

    target_ax.set_ylim(y_lo_lim, y_hi_lim)
    set_ylabel(ylbl, ax=target_ax)
    if is_edges:
        target_ax.set_xlim(float(raw_bins[0]), float(raw_bins[-1]))

    return container


def plot_limit(
    x: ArrayLike,
    expected: ArrayLike,
    *,
    observed: ArrayLike | None = None,
    one_sigma: tuple[ArrayLike, ArrayLike] | None = None,
    two_sigma: tuple[ArrayLike, ArrayLike] | None = None,
    expected_label: str = "Expected (95% CL)",
    observed_label: str = "Observed (95% CL)",
    one_sigma_label: str = r"Expected $\pm 1\sigma$",
    two_sigma_label: str = r"Expected $\pm 2\sigma$",
    band_palette: Literal["faser", "atlas"] = "faser",
    ax: Axes | None = None,
    **kwargs: Any,
) -> dict[str, Artist]:
    """Plot a 1D Brazil-band upper limit curve."""
    if band_palette == "faser":
        c1, c2 = "faser:onesigma", "faser:twosigma"
    elif band_palette == "atlas":
        c1, c2 = "faser:atlas-onesigma", "faser:atlas-twosigma"
    else:
        raise ValueError(f"Unknown band_palette {band_palette!r}; expected 'faser' or 'atlas'.")

    target_ax = ax if ax is not None else plt.gca()
    x_arr = np.asarray(x, dtype=np.float64)
    exp_arr = np.asarray(expected, dtype=np.float64)

    artists: dict[str, Artist] = {}

    if two_sigma is not None:
        artists["two_sigma"] = plot_band(
            x_arr,
            two_sigma[0],
            two_sigma[1],
            label=two_sigma_label,
            color=c2,
            alpha=0.85,
            ax=target_ax,
            zorder=1,
        )

    if one_sigma is not None:
        artists["one_sigma"] = plot_band(
            x_arr,
            one_sigma[0],
            one_sigma[1],
            label=one_sigma_label,
            color=c1,
            alpha=0.90,
            ax=target_ax,
            zorder=2,
        )

    exp_kwargs = dict(kwargs)
    exp_kwargs.setdefault("linestyle", "--")
    exp_kwargs.setdefault("color", "faser:exp-limit")
    exp_kwargs.setdefault("linewidth", 1.8)
    exp_kwargs.setdefault("zorder", 3)
    (exp_line,) = target_ax.plot(x_arr, exp_arr, label=expected_label, **exp_kwargs)
    artists["expected"] = exp_line

    if observed is not None:
        obs_arr = np.asarray(observed, dtype=np.float64)
        (obs_line,) = target_ax.plot(
            x_arr,
            obs_arr,
            linestyle="-",
            marker="o",
            markersize=5.5,
            color="faser:data",
            linewidth=2.0,
            label=observed_label,
            zorder=4,
        )
        artists["observed"] = obs_line

    return artists


def _build_contour_poly(
    x: ArrayLike,
    y_low: ArrayLike,
    y_high: ArrayLike | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert either a polygon ``(x, y)`` or envelope ``(x, y_low, y_high)`` into polygon vertices."""
    x_arr = np.asarray(x, dtype=np.float64)
    lo_arr = np.asarray(y_low, dtype=np.float64)
    if y_high is None:
        return (x_arr, lo_arr)
    hi_arr = np.asarray(y_high, dtype=np.float64)
    px = np.concatenate([x_arr, x_arr[::-1]])
    py = np.concatenate([lo_arr, hi_arr[::-1]])
    return (px, py)


def plot_exclusion(
    x: ArrayLike,
    y_low: ArrayLike,
    y_high: ArrayLike | None = None,
    *,
    expected: tuple[ArrayLike, ArrayLike] | tuple[ArrayLike, ArrayLike, ArrayLike] | None = None,
    one_sigma: tuple[ArrayLike, ArrayLike, ArrayLike] | tuple[ArrayLike, ArrayLike] | None = None,
    observed_label: str = "Observed Limit (90% CL)",
    expected_label: str = r"Expected Limit ($\pm 1\sigma_{\mathrm{exp}}$, 90% CL)",
    existing: Sequence[dict[str, Any]] | None = None,
    existing_label: str | None = "Existing Limits",
    color: str = "faser:obs-limit",
    expected_color: str = "faser:exp-limit",
    band_color: str = "faser:onesigma",
    hatch: str | None = None,
    fill_alpha: float = 0.0,
    linewidth: float = 2.0,
    ax: Axes | None = None,
) -> dict[str, Any]:
    """Plot a 2D BSM parameter-space exclusion contour in canonical FASER style."""
    target_ax = ax if ax is not None else plt.gca()
    artists: dict[str, Any] = {}

    if existing is not None:
        existing_artists: list[Artist] = []
        used_existing_label = False
        for entry in existing:
            ex = entry["x"]
            if "y_low" in entry and "y_high" in entry:
                px, py = _build_contour_poly(ex, entry["y_low"], entry["y_high"])
            else:
                px, py = _build_contour_poly(ex, entry["y"])

            lbl = existing_label if (not used_existing_label and existing_label) else None
            used_existing_label = True
            (poly,) = target_ax.fill(
                px,
                py,
                facecolor=entry.get("facecolor", "faser:existing-fill"),
                edgecolor=entry.get("edgecolor", "faser:existing-edge"),
                linewidth=float(entry.get("linewidth", 0.8)),
                alpha=float(entry.get("alpha", 0.85)),
                label=lbl,
                zorder=1,
            )
            existing_artists.append(poly)

            if entry.get("label") and entry.get("text_pos") is not None:
                tx, ty = entry["text_pos"]
                txt = target_ax.text(
                    float(tx),
                    float(ty),
                    str(entry["label"]),
                    color=entry.get("text_color", "faser:existing-text"),
                    fontsize=float(entry.get("fontsize", float(mpl.rcParams["font.size"]) * 0.82)),
                    rotation=float(entry.get("rotation", 0.0)),
                    ha="center",
                    va="center",
                    zorder=2,
                )
                existing_artists.append(txt)
        artists["existing"] = existing_artists

    if one_sigma is not None:
        if len(one_sigma) == 3:
            sx, slo, shi = one_sigma
            px, py = _build_contour_poly(sx, slo, shi)
        else:
            sx, sy = one_sigma
            px, py = _build_contour_poly(sx, sy)
        (band_poly,) = target_ax.fill(
            px,
            py,
            facecolor=band_color,
            edgecolor="none",
            alpha=0.85,
            label=expected_label if expected is None else None,
            zorder=2,
        )
        artists["one_sigma"] = band_poly

    if expected is not None:
        if len(expected) == 3:
            ex_x, ex_lo, ex_hi = expected
            px, py = _build_contour_poly(ex_x, ex_lo, ex_hi)
            px = np.append(px, px[0])
            py = np.append(py, py[0])
        else:
            px = np.asarray(expected[0], dtype=np.float64)
            py = np.asarray(expected[1], dtype=np.float64)
        (exp_line,) = target_ax.plot(
            px,
            py,
            linestyle="--",
            color=expected_color,
            linewidth=max(linewidth - 0.3, 1.2),
            label=expected_label,
            zorder=3,
        )
        artists["expected"] = exp_line

    px_obs, py_obs = _build_contour_poly(x, y_low, y_high)
    if y_high is not None and px_obs.size > 0:
        px_line = np.append(px_obs, px_obs[0])
        py_line = np.append(py_obs, py_obs[0])
    else:
        px_line, py_line = px_obs, py_obs

    if hatch is not None or fill_alpha > 0.0:
        fc: Any = mcolors.to_rgba(color, fill_alpha) if fill_alpha > 0.0 else "none"
        ec: Any = color if hatch is not None else "none"
        (obs_fill,) = target_ax.fill(
            px_obs,
            py_obs,
            facecolor=fc,
            edgecolor=ec,
            hatch=hatch,
            linewidth=0.0,
            zorder=4,
        )
        artists["observed_fill"] = obs_fill

    (obs_line,) = target_ax.plot(
        px_line,
        py_line,
        linestyle="-",
        color=color,
        linewidth=linewidth,
        label=observed_label,
        zorder=5,
    )
    artists["observed"] = obs_line
    return artists


def plot_2d(
    xbins: ArrayLike,
    ybins: ArrayLike,
    values: ArrayLike,
    *,
    cmap: str = "viridis",
    norm: mcolors.Normalize | None = None,
    logz: bool = False,
    vmin: float | None = None,
    vmax: float | None = None,
    zlabel: str | None = None,
    colorbar: bool = True,
    cbar_pad: float = 0.03,
    cbar_size: str = "4.5%",
    rasterized: bool = True,
    ax: Axes | None = None,
    **kwargs: Any,
) -> tuple[QuadMesh, Colorbar | None]:
    """Plot a 2D binned histogram / heatmap via ``pcolormesh`` with matched-height colorbar.

    Follows Matplotlib's ``pcolormesh(xbins, ybins, values)`` convention where
    ``values`` has shape ``(len(ybins) - 1, len(xbins) - 1)``.
    """
    target_ax = ax if ax is not None else plt.gca()
    xb = np.asarray(xbins, dtype=np.float64)
    yb = np.asarray(ybins, dtype=np.float64)
    vals = np.asarray(values, dtype=np.float64)

    mesh_kwargs = dict(kwargs)
    mesh_kwargs["cmap"] = cmap
    mesh_kwargs["rasterized"] = rasterized

    plot_vals: np.ndarray | np.ma.MaskedArray
    if logz and norm is None:
        masked = np.ma.masked_less_equal(vals, 0.0)
        positive = masked.compressed()
        if positive.size > 0:
            lo = float(vmin) if (vmin is not None and vmin > 0.0) else float(np.min(positive))
            hi = float(vmax) if (vmax is not None and vmax > 0.0) else float(np.max(positive))
            if hi <= lo:
                hi = lo * 10.0
            norm = mcolors.LogNorm(vmin=lo, vmax=hi)
        else:
            norm = mcolors.LogNorm(vmin=1e-1, vmax=1.0)
        plot_vals = masked
    else:
        plot_vals = vals

    if norm is not None:
        mesh_kwargs["norm"] = norm
    else:
        if vmin is not None:
            mesh_kwargs["vmin"] = vmin
        if vmax is not None:
            mesh_kwargs["vmax"] = vmax

    mesh = target_ax.pcolormesh(xb, yb, plot_vals, **mesh_kwargs)

    cbar: Colorbar | None = None
    if colorbar:
        divider = make_axes_locatable(target_ax)
        cax = divider.append_axes("right", size=cbar_size, pad=cbar_pad)
        cbar = target_ax.figure.colorbar(mesh, cax=cax)
        if zlabel is not None:
            set_zlabel(zlabel, cbar)

    return (mesh, cbar)
