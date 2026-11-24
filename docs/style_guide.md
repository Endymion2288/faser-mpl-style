# FASER Collaboration Plotting Style Guide

This guide documents the empirical design principles behind `faser-mpl-style`, grounded in a quantitative and visual audit of all **13 published FASER Collaboration papers** (`arXiv:2303.14185`–`arXiv:2611.03904`, 176 physics figures) and harmonized with modern ATLAS/LHC conventions (`atlas-mpl-style` and `mplhep.style.ATLAS`).

---

## 1. Empirical Foundation

Across 111 vector physics PDFs and 65 raster figures from all 13 papers:

- **Tooling convergence**: 72 vector figures are Matplotlib-family (50 native Matplotlib + 22 Cairo-backend in `2412.03186`) and 36 are ROOT-family. Recent flagship Matplotlib plots (`2308.05587`, `2410.10363`, `2607.26195`, `2611.03904`) intentionally match the ATLAS/ROOT visual grammar (4-sided inward ticks, minor ticks on, right/top axis labels, Helvetica-like sans-serif typography) while leveraging Matplotlib's shading, hatching, and perceptual colormaps.
- **Universal structural norms**:
  - **Closed 4-spine frame** (`0.75–1.0 pt` black spines): ~100% of physics figures.
  - **Frameless legends** (`legend.frameon = False`): 99% of figures (`72/72` Matplotlib+Cairo, `25/26` ROOT).
  - **No background grid** (`axes.grid = False`): ~90% of figures.
  - **Opaque white background**: 100% of figures.
- **Solved legacy defect (opaque logo box)**: In several published figures (`2410.10363`, `2602.17575`), embedding a Keynote-exported `FaserLogo.pdf` or 8-bit `FaserLogo.png` introduces an opaque white rectangle that clips top ticks and punches a hole through underlying data. `faser-mpl-style` bundles a high-resolution (`1800 px` source render, tight-cropped) **true transparent RGBA** logo with zero white halos and DPI-invariant sizing.

---

## 2. Design Decisions vs. `atlas-mpl-style`, `mplhep`, and Legacy `set_atlas()`

| Property | `atlas-mpl-style` | `mplhep.style.ATLAS` | Legacy `set_atlas()` | **`faser.mplstyle` (Canonical)** | Why |
|---|---|---|---|---|---|
| `figure.figsize` | `11.11 × 8.33` | `8.0 × 6.0` | `6.0 × 6.0` | **`8.0 × 6.0`** (`6.0 × 6.0` in `faser-square`) | Matches FASER median aspect ratio (`1.22–1.39`) and `mplhep`; `faser-square` serves 2-up journal panels. |
| `figure.dpi` / `savefig.dpi` | `72` / default | `100` / default | `100` / default | **`150` / `300`** | Sharp interactive/notebook viewing and print-ready PNG exports. |
| `savefig.facecolor` | Transparent | White | Auto | **`white`** | Prevents invisible black axes on dark-theme viewers, Jupyter dark mode, and slides. |
| `font.size` / `axes.labelsize` / `tick.labelsize` / `legend.fontsize` | `18 / 20 / 18 / 18` | `14 / 20.2 / 16.8 / 14` | `18 / 20 / 18 / 19` | **`15 / 18 / 15 / 14`** (`17 / 20 / 17 / 16` in `faser-talk`) | Clear `1.2×` axis-to-tick hierarchy; legend stays sleek and never larger than tick labels. |
| `xaxis/yaxis.labellocation` | Center (helpers move) | `right` / `top` | `center` | **`right` / `top`** | Authentic ATLAS/FASER alignment natively with standard `ax.set_xlabel` / `ax.set_ylabel`. |
| `xtick.top` / `ytick.right` | `True` / `True` | `True` / `True` | `False` / `False` | **`True` / `True`** (`ticks="bl"` opt-out) | Matches flagship BSM/stacked/limit plots; `ticks="bl"` or `faser-atlas-compat` disables top/right ticks cleanly. |
| `xtick/ytick.major.size` & `minor.size` | `5 / 3` | `5 / 3` (x), `14 / 7` (y) | `12 / 6` (x), `14 / 7` (y) | **`8.0 / 4.0`** symmetric | Clearly visible inward ticks on linear and log axes without colliding with ratio-panel data. |
| `xtick/ytick.minor.visible` | `True` | `True` | `False` | **`True`** | Required for log-scale energy/coupling plots and standard HEP histograms. |
| `text.usetex` | `True` in `.mplstyle` | `False` | `False` | **`False`** (safe opt-in `usetex=True`) | Zero TeX toolchain dependency out of the box; `use_faser_style(usetex=True)` verifies binaries first. |
| `mathtext` setup | `Tex Gyre Heros` | `TeX Gyre Heros` | Bare `Helvetica`, `rm: serif` | **`custom`**, `rm/sf: sans`, `it: sans:italic`, `bf: sans:bold`, `bfit: sans:italic:bold`, `default: it`, `fallback: stixsans` | Generic `sans` resolves via `font.sans-serif` with **zero `findfont` warnings** on every OS, keeps `\mathrm{GeV}` sans-serif, and renders Greek/operators cleanly. |
| `axes.formatter.limits` | `-2, 4` | `-2, 4` | `-5, 6` | **`-3, 4`** (`use_mathtext: True`) | Keeps `1000` (e.g. `1000 GeV`) plain while cleanly formatting `10^4+` with sans-serif powers. |
| `lines.linewidth` / `markersize` | `1.5` / `6.0` | `2.0` / `8.0` | `1.0` / `8.0` | **`1.8` / `6.5`** | Clean print weight (fixes `set_atlas()`'s hair-thin `1.0 pt` curves). |
| `axes.prop_cycle` | Okabe–Ito (vermilion 1st, includes yellow) | Okabe–Ito / Petroff | Tab10 | **FASER Okabe–Ito 7** (blue `#0072B2` 1st, red `#D55E00` 2nd, no yellow) | Colorblind-safe AND honors FASER's universal blue-primary / red-secondary hierarchy. |

### Choosing a Style Preset

- **`faser`** *(default, `8.0 × 6.0`)*: Use for all standard journal figures, 1D distributions, exclusion contours, and 2D heatmaps.
- **`faser-square`** *(`6.0 × 6.0`)*: Use when placing two or three plots side by side in a LaTeX paper (`\subfigure` / `minipage`) so fonts remain crisp at reduced column width.
- **`faser-talk`** *(`8.0 × 5.5`)*: Use for conference slides, seminar talks, and group meetings (`17/20/17/16 pt` fonts, `1.2 pt` spines, `2.2 pt` curves).
- **`faser-atlas-compat`** *(`6.0 × 6.0`)*: Use when migrating legacy `set_atlas()` notebooks with minimal layout change (bottom/left ticks only, centered labels, `18/20/18/17 pt` typography, zero-warning font/mathtext stack).

---

## 3. Typography, Fonts & LaTeX

`faser-mpl-style` specifies an ordered cross-platform Helvetica-metric fallback list:

```text
TeX Gyre Heros, Helvetica Neue, Helvetica, Nimbus Sans, Nimbus Sans L,
Liberation Sans, Arial, FreeSans, DejaVu Sans
```

- Because `mathtext.rm`, `mathtext.sf`, `mathtext.it`, `mathtext.bf`, and `mathtext.bfit` all delegate to generic `sans` families with `mathtext.fallback: stixsans`, Matplotlib resolves whichever sans-serif font is installed on your system (macOS `Helvetica Neue`/`Helvetica`, Linux `TeX Gyre Heros`/`Nimbus Sans`/`Liberation Sans`, Windows `Arial`, or headless CI `DejaVu Sans`) with **zero `findfont` warnings**.
- Write upright units with `\mathrm{...}` (for example `r"$E_{\mathrm{cal}}\ [\mathrm{GeV}]$"` or `r"$p_\mu\ [\mathrm{GeV}]$"`): because `mathtext.rm: sans`, `\mathrm` stays seamlessly sans-serif rather than switching to serif.
- If you want full LaTeX rendering for final journal PDFs, pass `use_faser_style(usetex=True)`. If `pdflatex`/`latex`, `dvipng`, or `gs` is missing on the machine, `use_faser_style` emits a `UserWarning` and safely falls back to `text.usetex = False`.
- To switch fonts or scale all font sizes proportionally without breaking hierarchy, use `set_font(family=..., size=...)`.

---

## 4. Dual Collaboration Branding Rules

Unlike ATLAS (which uses only typographic bold-italic *`ATLAS`*), FASER papers establish **two official branding styles** across **two placements**:

### 4.1 Typographic ATLAS-Style Stamp (`draw_faser_label`)
Used in `2402.13318`, `2403.12520`, `2503.19775`, and `2602.17575` (and ideal whenever specifying sub-detectors like **`FASERν`** or **`FASER2`**):
- Renders bold-italic **`FASER`** (or **`FASERν`**) followed by regular status text, then `√s` and integrated luminosity (`L`) on line 2, and optional description lines below.
- Standard status strings (also accepted via short aliases in `STATUS_ALIASES`):
  - `""` / `"final"` / `"published"` → publication final (no status word)
  - `"Preliminary"` (`"prelim"`)
  - `"Internal"` (`"int"`)
  - `"Simulation"` (`"sim"`)
  - `"Simulation Preliminary"` (`"sim_prelim"`, or `simulation=True, status="prelim"`)
  - `"Simulation Internal"` (`"sim_int"`)
  - `"Work in Progress"` (`"wip"`)
  - `"Testbeam"` / `"Test Beam"` (`"testbeam"`, `"test beam"`)

### 4.2 Graphical Transparent `FaserLogo` (`draw_faser_logo` or `draw_faser_label(..., style="logo")`)
Used in **9 of 13 published papers** (`2308`, `2403`, `2410`, `2504`, `2507`, `2602`, `2606`, `2607`, `2611`):
- **`layout="stacked"`** *(default)*: Status, `√s`, `L`, and description lines stacked directly beneath the swooshed emblem (e.g., `2308.05587`, `2410.10363`, `2611.03904`).
- **`layout="inline"`**: Status and metadata placed cleanly beside the emblem (e.g., `2607.26195/summary_limits_gray.png`).
- **Color tinting**: Use `color="black"` on light backgrounds, `color="white"` on dark `viridis`/`faser_bird` heatmaps or dark slides, or any Matplotlib / `faser:*` color such as `color="faser:blue"`.
- **DPI-invariant width**: `width=0.24` means 24% of the axes physical width regardless of whether you render at 100 DPI, 150 DPI, 300 DPI, PDF, or SVG.

### 4.3 Outside Top-Header Placement (`loc="outside"`)
Used in `2303.14185` (typographic) and `2412.03186` (graphical logo):
- Places `FASER [status]` or the transparent `FaserLogo` flush above the top-left spine and right-aligned `√s, L` above the top-right spine.
- **Recommended for 2D heatmaps, scatter plots, and dense distributions** where inside-axes space is scarce.

### 4.4 Headroom & Non-Overlapping Labels
- For inside-axes stamps (`loc="upper left"` / `"upper right"`), pass `pad_y=True` (default +25% headroom) or `pad_y=0.35` to expand y-axis limits automatically on **both linear and logarithmic scales**.
- Place the legend in the opposite upper corner from the FASER stamp (typically stamp at `"upper left"`, legend at `"upper right"`).

> **Branding Notice**: Official FASER logos and collaboration labels (`FASER`, `FASER Preliminary`, `FASERν`) should only appear on figures authorized by the FASER Collaboration.

---

## 5. Color Palettes, Semantic Colors & 2D Colormaps

### 5.1 Discrete Palettes (`FASER_PALETTES`)

| Palette | Hex Values | Best For |
|---|---|---|
| **`faser`** *(default)* | `#0072B2`, `#D55E00`, `#009E73`, `#E69F00`, `#CC79A7`, `#56B4E9`, `#595959` | Default colorblind-safe curve cycle (blue first, red second, no yellow on white). Automatically upgrades to `petroff8`/`petroff10` via `get_palette("faser", n)` when `n > 7`. |
| **`faser-tango`** | `#3465A4`, `#CC0000`, `#F57900`, `#4E9A06`, `#75507B`, `#729FCF` | Multi-generator / flux comparisons with shaded bands (`arXiv:2412.03186`). |
| **`faser-stack`** | `#56B4E9`, `#FF6B6B`, `#7BC96F`, `#FFB347`, `#B39DDB`, `#A9B4C2` | Stacked filled MC histograms with black outlines and hatched error bands (`arXiv:2410.10363`). |
| **`faser-classic`** | `#0000FF`, `#FF0000`, `#009900`, `#FFA500`, `#9933CC`, `#00AACC` | High-contrast ROOT / FORESEE-style overlays. |
| **`atlas`** | `#D55E00`, `#56B4E9`, `#E69F00`, `#F0E442`, `#009E73`, `#CC79A7`, `#0072B2` | Exact `atlas-mpl-style` / `mplhep.style.ATLAS` Okabe–Ito sequence. |
| **`petroff6`** | `#5790FC`, `#F89C20`, `#E42536`, `#964A8B`, `#9C9CA1`, `#7A21DD` | Accessible 6-color sequence (`arXiv:2107.02270`). |
| **`petroff8`** | `#1845FB`, `#FF5E02`, `#C91F16`, `#C849A9`, `#ADAD7D`, `#86C8DD`, `#578DFF`, `#656364` | Accessible 8-color sequence. |
| **`petroff10`** | `#3F90DA`, `#FFA90E`, `#BD1F01`, `#94A4A2`, `#832DB6`, `#A96B59`, `#E76300`, `#B9AC70`, `#717581`, `#92DADD` | Accessible 10-color sequence for complex multi-component breakdowns. |

### 5.2 Semantic Named Colors (`faser:*`)

Importing `faser_mpl_style` registers 22 named colors directly in Matplotlib:

- **Core series**: `faser:blue` (`#0072B2`), `faser:red` (`#D55E00`), `faser:green` (`#009E73`), `faser:orange` (`#E69F00`), `faser:purple` (`#CC79A7`), `faser:sky` (`#56B4E9`), `faser:coral` (`#FF6B6B`), `faser:gray` (`#595959`).
- **Tango accents**: `faser:tango-blue` (`#3465A4`), `faser:tango-red` (`#CC0000`), `faser:tango-orange` (`#F57900`).
- **Data & uncertainties**: `faser:data` (`#000000`), `faser:unc-band` (`#7F7F7F`).
- **Limits & exclusions**: `faser:obs-limit` (`#0033FF`), `faser:exp-limit` (`#333333`), `faser:onesigma` (`#B9FF61`), `faser:twosigma` (`#FFF57A`), `faser:atlas-onesigma` (`#00FF26`), `faser:atlas-twosigma` (`#FBFF1F`), `faser:existing-fill` (`#D9D9D9`), `faser:existing-edge` (`#8C8C8C`), `faser:existing-text` (`#666666`).

### 5.3 2D Colormaps

- **`viridis`** *(default)*: Perceptually uniform sequential colormap (`2412.03186`).
- **`faser_bird`** (and `"faser_bird_r"`, plus `"bird"` alias when unclaimed): Exact 10-stop replica of ROOT `kBird` (`2504.13008`, `2602.17575`).
- **`faser_blues`** (and `"faser_blues_r"`): Pure-white-zero to deep-navy sequential density map (`2607.26195`), ideal when overlaying colored MC markers or black selection contours on top of 2D data histograms.

---

## 6. Canonical FASER Plot Archetypes & Recipes

### 6.1 Stacked MC + Data + Ratio Panel (`2410.10363`, `2412.03186`)
- Use `ratio_axes()` to create a 3:1 main/ratio layout with `hspace=0.06` and linked label alignment.
- Draw stacked MC backgrounds with `plot_mc_stack(..., err_style="hatch")` (`faser-stack` fills + crisp `0.8 pt` black borders + diagonal `////` `Stat. ⊕ Syst.` band).
- Overlay data using `plot_data(..., yerr="poisson", show_zero=False)` for exact Garwood 68.27% CL bars without cluttering empty bins.
- Populate the lower panel with `plot_ratio(..., mode="ratio")` (or `mode="diff"` / `mode="pull"`), echoing the hatched MC uncertainty band around `1.0` and automatically drawing red off-scale carets for out-of-range points.
- Call `set_xlabel(..., ax=ax)` on the main axes—it forwards automatically to the bottom ratio panel—and `set_ylabel` on both panels to keep y-labels vertically aligned.

### 6.2 2D BSM Exclusion Contours (`2308.05587`, `2410.10363`, `2607.26195`, `2611.03904`)
- Use log-log axes (`ax.set_xscale("log")`, `ax.set_yscale("log")`) with 4-sided inward major+minor ticks and no grid.
- Pass prior constraints via `plot_exclusion(..., existing=[...])` so existing bounds appear in neutral gray (`#D9D9D9` fill, `#8C8C8C` edge) with direct muted-gray experiment labels (`KLOE`, `BaBar`, `NA64`, `E141`, ...).
- Plot the expected contour as a dashed dark-gray curve surrounded by the signature FASER lime-green (`#B9FF61`) `±1σ` band.
- Plot the observed 90%/95% CL contour in vivid solid blue (`#0033FF`), optionally adding `hatch="//"` inside the excluded region (`2611.03904`).
- Stamp the figure with the transparent `draw_faser_logo(...)` (never an opaque white box).

### 6.3 1D Brazil-Band Upper Limits + Ratio (`2607.26195`)
- Use `plot_limit(x, expected, observed=..., one_sigma=..., two_sigma=..., band_palette="faser")` (or `band_palette="atlas"` for classic `#00FF26`/`#FBFF1F` green/yellow bands).
- Pair with `ratio_axes()` and `plot_ratio` when displaying signal-strength ratios ($\mu = \sigma_{\mathrm{limit}} / \sigma_{\mathrm{theory}}$).

### 6.4 2D Detector Efficiency & Calorimeter Heatmaps (`2412.03186`, `2504.13008`, `2602.17575`)
- Use `plot_2d(xbins, ybins, values, cmap="faser_bird", zlabel="Efficiency")` or `cmap="viridis", logz=True`.
- `plot_2d` automatically matches colorbar height to the axes frame, masks `<= 0` entries safely under `logz=True`, and top-aligns the colorbar label (`set_zlabel`).
- Use `draw_faser_logo(ax=ax, loc="outside", lumi=65.6)` or `draw_faser_label(..., loc="outside")` so 100% of the 2D heatmap stays unobstructed.
