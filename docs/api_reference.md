# API Reference

Complete reference for all public symbols exported in `faser_mpl_style.__all__`.

Importing `faser_mpl_style` performs three idempotent setup actions automatically:
1. Registers the bundled `.mplstyle` directory with Matplotlib's style library (`"faser"`, `"faser-square"`, `"faser-talk"`, `"faser-atlas-compat"`).
2. Registers all `faser:<name>` named colors via `register_colors()`.
3. Registers custom colormaps (`"faser_bird"`, `"faser_bird_r"`, `"faser_blues"`, `"faser_blues_r"`, and `"bird"` if unclaimed) via `register_colormaps()`.

---

## Version & Discovery

### `__version__: str`
Package semantic version string (e.g. `"0.1.0"`).

### `STYLES: tuple[str, ...]`
Tuple of bundled style preset names:

```python
("faser", "faser-square", "faser-talk", "faser-atlas-compat")
```

All four presets can also be loaded without importing `faser_mpl_style` via dotted Matplotlib style paths (`"faser_mpl_style.faser"`, `"faser_mpl_style.faser-square"`, `"faser_mpl_style.faser-talk"`, `"faser_mpl_style.faser-atlas-compat"`).

---

## Style Management (`faser_mpl_style.style`)

### `get_style_dict`
```python
def get_style_dict(preset: str = "faser") -> dict[str, Any]
```
Load and return a preset stylesheet as a plain `rcParams` dictionary without mutating global `matplotlib.rcParams`. Raises `ValueError` if `preset` is unknown and not an existing stylesheet path.

### `use_faser_style`
```python
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
) -> None
```
Apply a FASER Matplotlib style preset globally with optional overrides.

- **`preset`**: One of `STYLES` or path to a custom `.mplstyle` file. Raises `ValueError` on unknown preset.
- **`palette`**: Named palette from `FASER_PALETTES` or explicit sequence of colors applied via `set_color_cycle`.
- **`usetex`**: If `True`, checks `shutil.which` for `pdflatex` (or `latex`), `dvipng`, and `gs`. If any executable is missing, emits a `UserWarning` and keeps `text.usetex = False`; otherwise enables `text.usetex = True` with a sans-serif LaTeX preamble (`tgheros`/`helvet` + `amsmath`).
- **`ticks`**: When `None` (default), preserves each stylesheet's default (`"all"` for `faser`, `faser-square`, and `faser-talk`; `"bl"` for `faser-atlas-compat`). Passing `"all"` forces inward ticks on all 4 spines (`xtick.top = True`, `ytick.right = True`); `"bl"` limits ticks to bottom and left spines only.
- **`minor_ticks`**: When not `None`, explicitly sets `xtick.minor.visible` and `ytick.minor.visible`.
- **`fancy_legend`**: If `True`, enables framed rounded legends (`legend.frameon = True`, `legend.fancybox = True`).
- **`font_size`**: If given, proportionally scales all font size `rcParams` via `set_font(size=font_size)`.
- **`figsize`**: Optional `(width, height)` in inches overriding `figure.figsize`.
- **`rc`**: Optional mapping of arbitrary `rcParams` overrides applied last.

### `style_context`
```python
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
) -> Iterator[None]
```
Context manager that applies `use_faser_style(...)` for the duration of the `with` block and restores the previous `matplotlib.rcParams` cleanly on exit.

### `set_font`
```python
def set_font(
    family: str | Sequence[str] | None = None,
    size: float | None = None,
) -> None
```
Prepend one or more font family names to `font.sans-serif` and/or proportionally scale all numeric font size `rcParams` (`font.size`, `axes.titlesize`, `axes.labelsize`, `xtick.labelsize`, `ytick.labelsize`, `legend.fontsize`, `legend.title_fontsize`, `figure.titlesize`, `figure.labelsize`) by `size / rcParams["font.size"]`. Emits a `UserWarning` if `family` is passed while `text.usetex` is `True`.

### `reset_style`
```python
def reset_style() -> None
```
Restore Matplotlib's built-in default `rcParams` via `matplotlib.rcdefaults()`.

---

## Colors & Colormaps (`faser_mpl_style.colors`)

### `FASER_COLORS: dict[str, str]`
Dictionary mapping short semantic names (without the `"faser:"` prefix, e.g. `"blue"`, `"red"`, `"obs-limit"`, `"onesigma"`, `"existing-fill"`) to hex color strings.

### `FASER_PALETTES: dict[str, list[str]]`
Dictionary of curated discrete color palettes:
`"faser"`, `"faser-tango"`, `"faser-stack"`, `"faser-classic"`, `"atlas"`, `"petroff6"`, `"petroff8"`, and `"petroff10"`.

### `get_palette`
```python
def get_palette(name: str = "faser", n: int | None = None) -> list[str]
```
Return a list of hex colors for a named palette.
- Performs case-insensitive lookup (also accepts `"petroff"` to auto-select `petroff6` / `petroff8` / `petroff10` based on `n`).
- For `name == "faser"` with `n` specified: uses the first `n` colors of `FASER_PALETTES["faser"]` for `n <= 7`, `petroff8` for `n == 8`, and `petroff10` (cycled if `n > 10`) for `n >= 9`.
- For other palettes, slices to `n` (or repeats cyclically if `n > len(palette)`).
- Raises `KeyError` / `ValueError` listing available palette names if unknown.

### `set_color_cycle`
```python
def set_color_cycle(
    palette: str | Sequence[str] = "faser",
    n: int | None = None,
    *,
    ax: Axes | None = None,
) -> list[str]
```
Set Matplotlib's `axes.prop_cycle` globally (`ax=None`) or on a specific `Axes` instance. Returns the resolved list of colors applied.

### `register_colors`
```python
def register_colors() -> None
```
Idempotently register every color in `FASER_COLORS` into Matplotlib's named color table under the `"faser:<name>"` prefix (e.g. `"faser:blue"`, `"faser:onesigma"`).

### `register_colormaps`
```python
def register_colormaps() -> None
```
Idempotently register `"faser_bird"`, `"faser_bird_r"`, `"faser_blues"`, `"faser_blues_r"`, and the `"bird"` alias (if not already present) into `matplotlib.colormaps`.

---

## Collaboration Branding & Labels (`faser_mpl_style.labels`)

### `STATUS_ALIASES: dict[str, str]`
Case-insensitive mapping of shorthand status keywords (`""`, `"final"`, `"published"`, `"prelim"`, `"preliminary"`, `"int"`, `"internal"`, `"sim"`, `"simulation"`, `"sim_prelim"`, `"sim-prelim"`, `"simulation preliminary"`, `"sim_int"`, `"sim-int"`, `"simulation internal"`, `"wip"`, `"work in progress"`, `"testbeam"`, `"test beam"`) to canonical display strings.

### `draw_faser_label`
```python
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
) -> list[Artist]
```
Draw a FASER collaboration stamp (typographic or graphical logo) with optional status, center-of-mass energy, luminosity, and extra description lines.

- **`x, y`**: Optional explicit anchor in axes fraction coordinates; when omitted, chosen from `loc`.
- **`ax`**: Target `Axes` (defaults to `plt.gca()`).
- **`experiment`**: `"FASER"` (default), `"FASERv"` / `"FASERν"`, `"FASER2"`, or custom string.
- **`status` / `simulation`**: Resolves `status` through `STATUS_ALIASES` (unknown non-empty strings kept verbatim). Setting `simulation=True` prepends `"Simulation"` if not already present.
- **`com` / `lumi` / `lumi_unit` / `lumi_prefix`**: Numeric `com=13.6` formats as `$\sqrt{s} = 13.6\ \mathrm{TeV}$`; numeric `lumi=65.6` formats with `lumi_prefix="L"` (`$L = ...$`), `"calL"` (`$\mathcal{L} = ...$`), or `""` (plain `$65.6\ \mathrm{fb}^{-1}$`). String `lumi` is used verbatim.
- **`desc`**: Single string or sequence of additional annotation lines rendered underneath.
- **`loc`**: `"upper left"`, `"upper right"`, `"lower left"`, `"lower right"`, or `"outside"` (places experiment/status above top-left spine and `com, lumi` above top-right spine).
- **`style`**: `"text"` (default, typographic bold-italic header + subtext `Text` artists) or `"logo"` (delegates to `draw_faser_logo`).
- **`pad_y`**: If `True` (expands by `0.25`) or a positive float, calls `expand_ylim` to reserve headroom without overlapping data.
- **Returns**: List of created Matplotlib `Artist` objects.

### `draw_faser_logo`
```python
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
) -> list[Artist]
```
Draw the bundled transparent RGBA graphical FASER emblem onto `ax` with DPI-invariant width (`width` as a fraction of the axes physical width), runtime RGB color tinting (`color`, `alpha`), and optional status, `com`/`lumi`, and `desc` text packed in `"stacked"` or `"inline"` layout (or `"outside"` top-header bar). Returns the list of created Matplotlib `Artist` objects.

### `expand_ylim`
```python
def expand_ylim(
    ax: Axes | None = None,
    fraction: float = 0.25,
    *,
    top: bool = True,
    bottom: bool = False,
) -> tuple[float, float]
```
Expand the visible y-axis limits by `fraction` of the current range (linearly on linear axes, and multiplicatively in $\log_{10}$ space on log axes). Returns the new `(ymin, ymax)` tuple.

### `set_xlabel`
```python
def set_xlabel(label: str, ax: Axes | None = None, **kwargs: Any) -> Text
```
Set a right-aligned ATLAS/FASER x-axis label. If `ax` is a main axes created by `ratio_axes()`, automatically forwards the label to the bottom-most linked ratio panel.

### `set_ylabel`
```python
def set_ylabel(label: str, ax: Axes | None = None, **kwargs: Any) -> Text
```
Set a top-aligned ATLAS/FASER y-axis label and call `fig.align_ylabels(...)` across any linked ratio panels.

### `set_zlabel`
```python
def set_zlabel(label: str, cbar: Colorbar, **kwargs: Any) -> Text
```
Set a top-aligned label on a Matplotlib `Colorbar` axis.

### `draw_tag`
```python
def draw_tag(
    text: str,
    ax: Axes | None = None,
    *,
    fontsize: float | None = None,
    **kwargs: Any,
) -> Text
```
Draw a small right-aligned metadata or version tag directly above the top-right corner of `ax`.

---

## High-Level HEP Plotting Utilities (`faser_mpl_style.plot`)

### `ratio_axes`
```python
def ratio_axes(
    figsize: tuple[float, float] | None = None,
    *,
    height_ratios: Sequence[float] | None = None,
    hspace: float = 0.06,
    extra_axes: int = 0,
    sharex: bool = True,
) -> tuple[Figure, Axes, Axes] | tuple[Figure, Axes, list[Axes]]
```
Create a publication-ready main + ratio figure (or main + `1 + extra_axes` stacked ratio panels).
- Default `height_ratios`: `(3.0, 1.0)` for one ratio panel; `(3.0, 1.0, 1.0, ...)` for `extra_axes >= 1`.
- Default `figsize`: scales current `rcParams["figure.figsize"]` vertically to `(w, h * (1 + 0.28 * n_ratio))`.
- Hides x-tick labels on upper panels while keeping inward ticks visible, prunes upper tick labels when `hspace == 0.0`, and links panels for automatic `set_xlabel`/`set_ylabel` forwarding and alignment.
- Returns `(fig, main_ax, ratio_ax)` when `extra_axes == 0`, else `(fig, main_ax, ratio_axes_list)`.

### `poisson_errors`
```python
def poisson_errors(
    counts: ArrayLike,
    *,
    method: Literal["garwood", "sqrt"] = "garwood",
    alpha: float = 0.31731050786291415,
) -> np.ndarray
```
Compute `(2, N)` `[lower, upper]` statistical error bars for non-negative Poisson bin counts.
- `method="garwood"` computes exact $1 - \alpha$ (default 68.27% CL) asymmetric Garwood intervals (zero-count upper error $= 1.84102\dots$). Uses `scipy.stats.chi2.ppf` when SciPy is installed and a built-in exact table ($N \le 50$) + Wilson–Hilferty approximation ($N > 50$) otherwise—requiring zero runtime dependency on SciPy.
- `method="sqrt"` returns symmetric $\sqrt{N}$ bars as shape `(2, N)`.
- Raises `ValueError` on negative counts.

### `plot_1d`
```python
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
) -> StepPatch
```
Plot a 1D binned step histogram via `ax.stairs` with optional interior fill (`fill=True`) and symmetric or `(2, N)` asymmetric uncertainty band (`yerr` with `band=True` or `band_hatch`). Tightens x-limits to `[bins[0], bins[-1]]` when `autolim=True`.

### `plot_data`
```python
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
) -> ErrorbarContainer
```
Plot binned experimental data points with error bars. Accepts either bin edges (`len == len(counts) + 1`) or bin centers (`len == len(counts)`). Supports `yerr="poisson"` (exact Garwood), `yerr="sqrt"`, explicit arrays, or `None`; `xerr=True` draws half bin widths when bin edges are passed; `show_zero=False` hides zero-count bins for clean log-scale plots.

### `plot_mc_stack`
```python
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
) -> tuple[np.ndarray, np.ndarray | None]
```
Plot stacked filled MC histograms with crisp borders and an optional total uncertainty band (`err_style="hatch"` for canonical diagonal `////` hatching or `"fill"` for translucent shading). Defaults colors to `get_palette("faser-stack", len(hists))`. Combines per-component `yerr` in quadrature if `total_err` is not supplied. Returns `(total, total_err)`.

### `plot_band`
```python
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
) -> PolyCollection
```
Plot a shaded or hatched uncertainty band for either continuous arrays (`len(x) == len(low)`) or binned step histograms (`len(x) == len(low) + 1`, automatically stepped cleanly across every bin). When `hatch` is set without an explicit facecolor, draws a transparent hatched band (`facecolor="none"`).

### `plot_ratio`
```python
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
) -> ErrorbarContainer
```
Plot a Data/MC ratio, fractional difference, or pull panel:
- `mode="ratio"`: `num / den` (`ref_line=1.0`, default `ylabel="Data / MC"`, `ylim=(0.5, 1.5)`).
- `mode="diff"`: `(num - den) / den` (`ref_line=0.0`, default `ylabel="(Data - MC) / MC"`, `ylim=(-0.5, 0.5)`).
- `mode="pull"`: `(num - den) / sigma_tot` (`ref_line=0.0`, default `ylabel="Pull"`, `ylim=(-3.5, 3.5)`, plus dashed `±1` and dotted `±2` reference lines).
- Safely masks zero denominators (`den == 0`), plots denominator uncertainty band around `ref_line`, and draws red caret indicators at the top/bottom axis edge for out-of-range points when `offscale_arrows=True`.

### `plot_limit`
```python
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
) -> dict[str, Artist]
```
Plot a 1D Brazil-band upper limit curve (`±2σ` band, `±1σ` band, dashed expected line, and optional solid observed curve with markers). `band_palette="faser"` uses `faser:onesigma` (`#B9FF61`) and `faser:twosigma` (`#FFF57A`); `band_palette="atlas"` uses `faser:atlas-onesigma` (`#00FF26`) and `faser:atlas-twosigma` (`#FBFF1F`). Returns a dict of created `Artist` objects keyed by `"two_sigma"`, `"one_sigma"`, `"expected"`, and `"observed"`.

### `plot_exclusion`
```python
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
) -> dict[str, Any]
```
Plot a 2D BSM parameter-space exclusion contour in canonical FASER style.
- **Observed contour**: Ordered polygon `(x, y_low)` when `y_high is None`, or lower/upper envelope `(x, y_low, y_high)`. Supports interior `hatch` (e.g. `"//"`) and/or `fill_alpha > 0`.
- **Expected contour & `±1σ` band**: Accepts either closed polygons `(xe, ye)` or envelopes `(xe, y_lo, y_hi)`.
- **Existing constraints**: Sequence of dicts containing `'x'` and `'y'` (or `'y_low'`, `'y_high'`), plus optional `'label'`, `'text_pos'` (`(tx, ty)`), and `'rotation'` (degrees). Drawn in `faser:existing-fill` (`#D9D9D9`) with `faser:existing-edge` (`#8C8C8C`) borders and `faser:existing-text` annotations.
- **Returns**: Dictionary of created Matplotlib artists.

### `plot_2d`
```python
def plot_2d(
    xbins: ArrayLike,
    ybins: ArrayLike,
    values: ArrayLike,
    *,
    cmap: str = "viridis",
    norm: matplotlib.colors.Normalize | None = None,
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
) -> tuple[QuadMesh, Colorbar | None]
```
Plot a 2D binned histogram or heatmap via `pcolormesh` with a matched-height right-side colorbar (`mpl_toolkits.axes_grid1.make_axes_locatable`) and top-aligned `zlabel`. When `logz=True` and `norm is None`, masks values `<= 0` safely with `np.ma.masked_less_equal` and builds a `LogNorm`. Supports `"viridis"`, `"faser_bird"` (`"bird"`), `"faser_blues"`, or any Matplotlib colormap. Returns `(mesh, cbar)`.
