# faser-mpl-style

**Publication-grade Matplotlib stylesheets, color palettes, and HEP plotting helpers tailored to the FASER Collaboration at CERN.**

`faser-mpl-style` codifies the visual conventions observed across all 13 published FASER Collaboration papers (`arXiv:2303.14185`–`arXiv:2611.03904`, 176 physics figures) and harmonizes them with modern ATLAS and LHC plotting standards (`atlas-mpl-style` and `mplhep`). It works out of the box on macOS, Linux, and Windows with **zero LaTeX installation required** and **zero Matplotlib `findfont` warnings**.

---

## Key Features

- **4 Self-Contained Stylesheets**: `faser` (default 4:3 publication), `faser-square` (6×6 for 2-up/3-up journal panels), `faser-talk` (high-legibility slides), and `faser-atlas-compat` (clean drop-in replacement for legacy `set_atlas()` scripts).
- **Zero-Import & Short-Name Discovery**: Use `plt.style.use("faser_mpl_style.faser")` without even importing the package, or `import faser_mpl_style as fms` to register short names (`plt.style.use("faser")`), semantic colors (`"faser:blue"`), and colormaps (`"faser_bird"`).
- **Dual Collaboration Branding**:
  - Typographic ATLAS-style **`FASER`** / **`FASERν`** stamps (`draw_faser_label`).
  - Bundled **true transparent RGBA** graphical FASER logo (`draw_faser_logo`) rendered cleanly from the collaboration vector master—eliminating the opaque white background box that clips ticks and data in legacy figures, with DPI-invariant sizing and runtime color tinting (`"black"`, `"white"`, `"faser:blue"`).
  - Both **inside-axes** (`"upper left"`, `"upper right"`, `"lower left"`, `"lower right"`) and **outside top-header** (`loc="outside"`) placements.
- **Curated Color Palettes & Colormaps**: Blue-first colorblind-safe Okabe–Ito default (`"faser"`), `"faser-tango"` (`2412.03186`), `"faser-stack"` (`2410.10363`), `"faser-classic"`, `"atlas"`, Petroff 6/8/10 palettes, 22 semantic `faser:*` named colors, ROOT `kBird` (`"faser_bird"` / `"bird"`), and white-to-navy `"faser_blues"`.
- **High-Level HEP Plotting Helpers**: `ratio_axes`, `poisson_errors` (exact Garwood intervals with zero SciPy dependency), `plot_1d`, `plot_data`, `plot_mc_stack`, `plot_band`, `plot_ratio` (`ratio`/`diff`/`pull` + off-scale carets), `plot_limit` (Brazil bands), `plot_exclusion` (2D BSM contours), and `plot_2d` (matched-height colorbar + top-aligned z-label).

---

## Installation

```bash
pip install faser-mpl-style
```

Optional extras:

```bash
# Optional SciPy acceleration for exact Garwood Poisson intervals (built-in fallback requires no SciPy)
pip install "faser-mpl-style[scipy]"

# Development & testing tools
pip install "faser-mpl-style[dev]"
```

Requires Python `>=3.9`, Matplotlib `>=3.7`, and NumPy `>=1.22`.

---

## Quick Start

### 1. Zero-Import Stylesheet Usage

No package import is required when using the dotted stylesheet path:

```python
import matplotlib.pyplot as plt

plt.style.use("faser_mpl_style.faser")

fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 4], label="Signal")
ax.set_xlabel(r"$E_{\nu}$ [GeV]")
ax.set_ylabel("Events / bin")
ax.legend()
```

### 2. Full API & Short-Name Style Registration

Importing `faser_mpl_style` automatically registers the short style names (`"faser"`, `"faser-square"`, `"faser-talk"`, `"faser-atlas-compat"`), the `faser:*` named colors, and the `"faser_bird"` / `"faser_blues"` colormaps:

```python
import faser_mpl_style as fms
import matplotlib.pyplot as plt

fms.use_faser_style("faser")          # or plt.style.use("faser")

# Temporarily switch styles without mutating global rcParams:
with fms.style_context("faser-talk", palette="faser-tango"):
    fig, ax = plt.subplots()
    ...
```

---

## Style Presets

| Preset | Dotted Name | `figsize` | Base / Label / Tick / Legend (pt) | Ticks & Label Alignment | Best For |
|---|---|---|---|---|---|
| **`faser`** *(default)* | `faser_mpl_style.faser` | `8.0 × 6.0` | `15 / 18 / 15 / 14` | 4-sided inward + minor ticks; right/top labels | Journal papers, single-column/full-width figures |
| **`faser-square`** | `faser_mpl_style.faser-square` | `6.0 × 6.0` | `15 / 18 / 15 / 14` | 4-sided inward + minor ticks; right/top labels | 2-up / 3-up side-by-side journal panels |
| **`faser-talk`** | `faser_mpl_style.faser-talk` | `8.0 × 5.5` | `17 / 20 / 17 / 16` | Thicker `1.2 pt` spines, `2.2 pt` lines, `7.5 pt` markers | Conference talks, slides, group meetings |
| **`faser-atlas-compat`** | `faser_mpl_style.faser-atlas-compat` | `6.0 × 6.0` | `18 / 20 / 18 / 17` | Bottom/left inward major ticks only; centered labels | Clean drop-in replacement for legacy `set_atlas()` scripts |

All presets use a cross-platform sans-serif font stack (`TeX Gyre Heros` → `Helvetica Neue` → `Helvetica` → `Nimbus Sans` → `Liberation Sans` → `Arial` → `DejaVu Sans`) with custom sans-serif `mathtext` (`mathtext.rm: sans`, `mathtext.default: it`, `mathtext.fallback: stixsans`) and opaque white backgrounds (`savefig.dpi = 300`, `savefig.facecolor = white`).

---

## Dual Collaboration Branding

Published FASER papers use both typographic ATLAS-style stamps and the graphical swooshed `FASER` emblem, placed either inside the frame or in an outside header bar above the top spine:

```python
import faser_mpl_style as fms
import matplotlib.pyplot as plt

fms.use_faser_style()
fig, ax = plt.subplots()

# 1) Typographic ATLAS-style stamp (supports "FASER", "FASERν", "FASER2", etc.)
fms.draw_faser_label(
    ax=ax,
    experiment="FASERν",
    status="Preliminary",          # aliases: "prelim", "int", "sim", "sim_prelim", "wip", ""
    com=13.6,                      # -> √s = 13.6 TeV
    lumi=65.6,                     # -> L = 65.6 fb^-1
    desc="Calorimeter Region",
    loc="upper left",
    pad_y=True,                    # auto-expands linear or log y-axis for clean headroom
)

# 2) Transparent graphical FASER logo inside axes (stacked or inline layout)
fms.draw_faser_logo(
    ax=ax,
    width=0.24,
    loc="upper left",
    status="Simulation",
    com=13.6,
    lumi=186,
    layout="stacked",              # or "inline" (as in 2607.26195)
    color="black",                 # or "white" on dark heatmaps, "faser:blue", etc.
)

# 3) Outside top-header branding (ideal for 2D heatmaps & dense distributions)
fms.draw_faser_logo(ax=ax, loc="outside", lumi=65.6)
```

---

## Color Palettes & Colormaps

- **Discrete Palettes (`fms.FASER_PALETTES`, `fms.get_palette(name, n)`, `fms.set_color_cycle(name)`)**:
  - `"faser"` *(default)*: Colorblind-safe Okabe–Ito reordered blue-first / red-second (`#0072B2`, `#D55E00`, `#009E73`, `#E69F00`, `#CC79A7`, `#56B4E9`, `#595959`); automatically switches to `"petroff8"` / `"petroff10"` when `n > 7`.
  - `"faser-tango"`: Extracted from `arXiv:2412.03186` (`#3465A4`, `#CC0000`, `#F57900`, `#4E9A06`, `#75507B`, `#729FCF`).
  - `"faser-stack"`: Pastel-vivid stacked histogram fills from `arXiv:2410.10363` (`#56B4E9`, `#FF6B6B`, `#7BC96F`, `#FFB347`, `#B39DDB`, `#A9B4C2`).
  - `"faser-classic"`: Classic high-contrast ROOT / FORESEE colors.
  - `"atlas"`, `"petroff6"`, `"petroff8"`, `"petroff10"`.
- **Semantic Named Colors (`faser:*`)**: `"faser:blue"`, `"faser:red"`, `"faser:green"`, `"faser:orange"`, `"faser:purple"`, `"faser:sky"`, `"faser:coral"`, `"faser:obs-limit"` (`#0033FF`), `"faser:exp-limit"`, `"faser:onesigma"` (`#B9FF61`), `"faser:twosigma"` (`#FFF57A`), `"faser:existing-fill"` (`#D9D9D9`), `"faser:unc-band"`, and more.
- **2D Colormaps**: `"viridis"` (default), `"faser_bird"` (exact ROOT `kBird` replica; also aliased as `"bird"` when free), and `"faser_blues"` (white-to-navy log density scale).

---

## High-Level Plotting Helpers

### Stacked MC + Data with Ratio Panel

```python
import numpy as np
import faser_mpl_style as fms

fms.use_faser_style("faser")
bins = np.linspace(100, 1100, 11)
mc_numu = np.array([42, 65, 58, 46, 33, 24, 17, 11, 7, 4], dtype=float)
mc_nue = np.array([12, 18, 16, 13, 9, 7, 5, 3, 2, 1], dtype=float)
data = np.array([55, 81, 77, 56, 44, 29, 23, 13, 10, 4], dtype=float)

fig, ax, ax_r = fms.ratio_axes()
total, total_err = fms.plot_mc_stack(
    bins,
    [mc_numu, mc_nue],
    labels=[r"$\nu_\mu + \bar{\nu}_\mu$", r"$\nu_e + \bar{\nu}_e$"],
    total_err=0.12 * (mc_numu + mc_nue),
    ax=ax,
)
fms.plot_data(bins, data, ax=ax)
fms.plot_ratio(bins, data, total, num_err=fms.poisson_errors(data), den_err=total_err, ax=ax_r)

fms.set_xlabel(r"$E_{\mathrm{cal}}$ [GeV]", ax=ax)
fms.set_ylabel("Events / 100 GeV", ax=ax)
fms.draw_faser_label(ax=ax, experiment="FASERν", com=13.6, lumi=65.6, pad_y=0.35)
ax.legend(loc="upper right")
```

### 2D BSM Exclusion Contours & 2D Heatmaps

- `fms.plot_exclusion(...)`: Renders canonical FASER 90%/95% CL exclusion contours with gray existing limits, dashed expected contour + signature `#B9FF61` `±1σ` band, and solid `#0033FF` observed boundary (with optional diagonal hatching).
- `fms.plot_limit(...)`: Renders 1D Brazil-band upper limits (`band_palette="faser"` or `"atlas"`).
- `fms.plot_2d(...)`: Renders 2D `pcolormesh` heatmaps with `logz=True` zero masking, matched-height colorbar, and top-aligned z-label.

See the [`examples/`](examples/) directory for 5 complete, runnable physics examples covering all plot types.

---

## Migrating from `atlas-mpl-style` or Legacy `set_atlas()`

- **From `atlas-mpl-style`**: Replace `ampl.use_atlas_style()` with `fms.use_faser_style()` and `ampl.draw_atlas_label(...)` with `fms.draw_faser_label(...)` or `fms.draw_faser_logo(...)`. To keep the exact `atlas-mpl-style` Okabe–Ito color order, pass `palette="atlas"`. Unlike `atlas-mpl-style`, `faser-mpl-style` does not require a system LaTeX installation by default (`usetex=True` is opt-in with graceful fallback) and uses an opaque white `savefig.facecolor`.
- **From custom `set_atlas()` snippets**: Replace your local helper with `fms.use_faser_style("faser-atlas-compat")` for near-identical `6×6` layout, bottom/left ticks, and centered labels—while fixing `Helvetica` `findfont` warnings, serif `\mathrm` math mismatches, oversized legend text, and thin `1.0 pt` lines. Or upgrade to the canonical 4-sided-tick `fms.use_faser_style("faser")` (or `use_faser_style("faser-square", ticks="bl")`).

---

## Documentation

- [FASER Plotting Style Guide](docs/style_guide.md) — Empirical design rationale from all 13 published FASER papers, palettes, dual branding rules, and plot recipes.
- [API Reference](docs/api_reference.md) — Complete reference for every public symbol in `faser_mpl_style`.
- [Changelog](CHANGELOG.md) — Release history.

---

## FASER Collaboration Branding & Logo Usage Notice

The Python source code and Matplotlib stylesheets in `faser-mpl-style` are distributed under the [MIT License](LICENSE).

The bundled emblem image (`src/faser_mpl_style/assets/faser_logo.png`) reproduces the official **FASER Collaboration** logo (CERN). **The FASER logo and official collaboration stamps (`FASER`, `FASER Preliminary`, `FASERν`, etc.) must only be applied to figures reviewed and authorized by the FASER Collaboration.** Independent phenomenology studies, personal notes, or unofficial plots using this stylesheet should omit the FASER logo and official experiment labels, or clearly indicate unofficial / simulation status.
