# Changelog

All notable changes to `faser-mpl-style` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-24

### Added
- **Four self-contained Matplotlib stylesheets** empirically derived from all 13 published FASER Collaboration papers (`arXiv:2303.14185`–`arXiv:2611.03904`):
  - `faser` (default 4:3 publication layout, 4-sided inward major+minor ticks, right/top axis labels, frameless legend, opaque white background, zero-warning sans-serif mathtext).
  - `faser-square` (compact `6×6` layout for 2-up/3-up journal panels).
  - `faser-talk` (high-legibility presentation stylesheet).
  - `faser-atlas-compat` (clean drop-in replacement for legacy `set_atlas()` scripts).
- **Dual stylesheet discovery**: zero-import dotted loading (`plt.style.use("faser_mpl_style.faser")`) and short-name loading after import (`plt.style.use("faser")`), plus `use_faser_style`, `style_context`, `get_style_dict`, `set_font`, and `reset_style`.
- **Dual FASER Collaboration branding**:
  - Typographic `draw_faser_label` supporting `FASER`, `FASERν`, `FASER2`, status aliases (`STATUS_ALIASES`), `simulation=True`, `com`, `lumi`, `desc`, `loc="outside"`, and `pad_y`.
  - Bundled high-resolution **true transparent RGBA** graphical logo (`assets/faser_logo.png`) rendered via `draw_faser_logo` with DPI-invariant sizing, `"stacked"` / `"inline"` / `"outside"` layouts, and runtime color tinting.
  - Axis & annotation utilities: `set_xlabel`, `set_ylabel`, `set_zlabel`, `draw_tag`, and `expand_ylim` (linear & log scale).
- **Curated color palettes, semantic colors, and 2D colormaps**:
  - `FASER_PALETTES`: `"faser"`, `"faser-tango"`, `"faser-stack"`, `"faser-classic"`, `"atlas"`, `"petroff6"`, `"petroff8"`, `"petroff10"`.
  - `FASER_COLORS` registered under the `"faser:"` prefix (`register_colors`), `get_palette`, and `set_color_cycle`.
  - Custom colormaps registered via `register_colormaps`: `"faser_bird"` / `"faser_bird_r"` (ROOT `kBird` replica, aliased as `"bird"` when free) and `"faser_blues"` / `"faser_blues_r"`.
- **High-level HEP plotting utilities**:
  - `ratio_axes`, `poisson_errors` (exact Garwood intervals with built-in SciPy-free fallback), `plot_1d`, `plot_data`, `plot_mc_stack`, `plot_band`, `plot_ratio` (`ratio`, `diff`, `pull` + off-scale carets), `plot_limit` (Brazil bands), `plot_exclusion` (2D BSM exclusion contours), and `plot_2d` (matched-height colorbar + `logz` masking).
- **Documentation & runnable examples**:
  - Comprehensive [style guide](docs/style_guide.md), complete [API reference](docs/api_reference.md), and 5 physics-authentic runnable showcase scripts in `examples/`.
