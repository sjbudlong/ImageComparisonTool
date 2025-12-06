# NVIDIA FLIP Integration Guide

## Overview

This guide covers the NVIDIA FLIP (FLaws in Luminance and Pixels) perceptual metric integration for the Image Comparison Tool. FLIP provides human-perception-based image comparison that more accurately reflects how people perceive differences compared to traditional metrics like SSIM.

## Table of Contents

- [What is FLIP?](#what-is-flip)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Understanding FLIP Metrics](#understanding-flip-metrics)
- [Visualization Options](#visualization-options)
- [Integration with Historical Tracking](#integration-with-historical-tracking)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)

## What is FLIP?

NVIDIA FLIP is an advanced perceptual image comparison metric that:

- **Models Human Visual System (HVS)**: Accounts for how humans actually perceive differences
- **Spatial Frequency Sensitivity**: Detects differences based on viewing distance and display characteristics
- **Luminance Adaptation**: Adjusts for brightness variations
- **Chrominance Handling**: Processes color differences perceptually
- **Superior to SSIM**: Provides more accurate assessment for rendering quality, VFX, and gaming

### When to Use FLIP

✅ **Recommended for:**
- 3D rendering quality assessment (VFX, animation, game cinematics)
- Visual regression testing for graphics applications
- Diagram and technical illustration comparison
- Any scenario where perceptual similarity matters more than pixel-exact matching

⚠️ **Less suitable for:**
- Simple pixel-perfect verification
- Text-heavy documents (use pixel diff instead)
- Scenarios where any pixel change must be detected

## Installation

### Basic Installation

FLIP is included as a standard dependency. To install:

1. **Install all dependencies:**
```bash
pip install -r requirements.txt
```

This will install `flip-evaluator>=1.0.0` along with all other required packages.

### Verify Installation

```python
python -c "import flip; print('FLIP installed successfully')"
```

## Quick Start

### Command Line

```bash
# Enable FLIP with default settings
python -m ImageComparisonSystem --enable-flip

# Enable FLIP with custom colormap
python -m ImageComparisonSystem --enable-flip --flip-colormaps viridis jet turbo

# Enable FLIP with custom viewing distance
python -m ImageComparisonSystem --enable-flip --flip-pixels-per-degree 42.0
```

### Python API

```python
from ImageComparisonSystem import Config, ImageComparator

# Create config with FLIP enabled
config = Config(
    base_dir="path/to/images",
    new_dir="new",
    known_good_dir="known_good",
    enable_flip=True,
    flip_pixels_per_degree=67.0,  # Default: 0.7m viewing distance
    flip_colormaps=["viridis", "jet"],
    flip_default_colormap="viridis"
)

# Run comparison
comparator = ImageComparator(config)
results = list(comparator.compare_all_streaming())

# Access FLIP metrics
for result in results:
    if "FLIP Perceptual Metric" in result.metrics:
        flip = result.metrics["FLIP Perceptual Metric"]
        print(f"Mean FLIP error: {flip['flip_mean']:.4f}")
        print(f"Quality: {flip['flip_quality_description']}")
```

### GUI

1. Launch the GUI: `python -m ImageComparisonSystem.ui`
2. Navigate to **"FLIP Perceptual Metric (Optional)"** section
3. Check **"Enable NVIDIA FLIP perceptual analysis"**
4. Configure:
   - **Pixels Per Degree**: 67.0 (default) or custom value
   - **Heatmap Colormaps**: Select one or more (viridis, jet, turbo, magma)
   - **Default Colormap**: Choose primary visualization colormap
5. Click **"Start Comparison"**

## Configuration

### FLIP Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_flip` | bool | `False` | Enable/disable FLIP analysis (opt-in) |
| `flip_pixels_per_degree` | float | `67.0` | Viewing distance parameter (see below) |
| `flip_colormaps` | list[str] | `["viridis"]` | Colormaps for heatmap visualization |
| `flip_default_colormap` | str | `"viridis"` | Primary colormap for reports |
| `show_flip_visualization` | bool | `True` | Include FLIP visualizations in reports |

### Pixels Per Degree (PPD) Calculation

PPD determines viewing distance and affects perceptual sensitivity:

```
PPD = (display_width_pixels / display_width_mm) * (viewing_distance_mm / 57.3)
```

**Common Values:**
- `67.0` - Default (0.7m from 24" 1080p display)
- `42.0` - 1.0m from 24" display
- `94.0` - 0.5m from 24" display (close viewing)

**Use Cases:**
- **Desktop Applications**: 67.0 (standard desktop viewing)
- **Cinema/TV**: 30-40 (farther viewing distance)
- **Mobile**: 80-100 (close viewing)
- **Print Preview**: 100+ (very close inspection)

### Colormap Options

Available colormaps for FLIP heatmap visualization:

- **`viridis`** (default): Perceptually uniform, colorblind-friendly
- **`jet`**: High contrast, rainbow spectrum
- **`turbo`**: Improved rainbow, better perceptual uniformity than jet
- **`magma`**: Dark background friendly, good for presentations

You can generate multiple colormaps simultaneously for different viewing preferences.

## Usage Examples

### Example 1: VFX Rendering QA

```python
config = Config(
    base_dir="/renders/project_x",
    new_dir="latest_render",
    known_good_dir="approved_frames",
    enable_flip=True,
    flip_pixels_per_degree=42.0,  # Cinema viewing distance
    flip_colormaps=["viridis", "turbo"],
    # Enable historical tracking for trend analysis
    enable_history=True,
    build_number="v1.2.3"
)

comparator = ImageComparator(config)
results = list(comparator.compare_all_streaming())

# Find frames with significant perceptual differences
for result in results:
    flip_metrics = result.metrics.get("FLIP Perceptual Metric", {})
    if flip_metrics.get("flip_mean", 0) > 0.15:
        print(f"⚠️ {result.filename}: {flip_metrics['flip_quality_description']}")
```

### Example 2: Parallel Processing

```python
config = Config(
    base_dir="/large_dataset",
    new_dir="new",
    known_good_dir="baseline",
    enable_flip=True,
    enable_parallel=True,
    max_workers=8  # Use 8 CPU cores
)

comparator = ImageComparator(config)
results = comparator.compare_all_parallel()  # Much faster for large datasets
```

### Example 3: Custom Composite Metric Weights

```python
from ImageComparisonSystem.history import CompositeMetricCalculator

# Emphasize FLIP over other metrics
custom_weights = {
    "flip": 0.40,        # 40% weight to FLIP
    "pixel_diff": 0.15,   # 15% to pixel difference
    "ssim": 0.15,         # 15% to SSIM
    "color_distance": 0.15,  # 15% to color
    "histogram": 0.15     # 15% to histogram
}

config = Config(
    base_dir="/images",
    new_dir="new",
    known_good_dir="known_good",
    enable_flip=True,
    enable_history=True,
    composite_metric_weights=custom_weights
)
```

## Understanding FLIP Metrics

### Metric Values

FLIP metrics returned for each comparison:

```python
{
    "flip_mean": 0.145,              # Mean perceptual error (0-1)
    "flip_max": 0.523,                # Maximum error in image
    "flip_percentile_95": 0.287,      # 95th percentile error
    "flip_percentile_99": 0.412,      # 99th percentile error
    "flip_weighted_median": 0.156,    # Median of non-zero errors
    "flip_error_map_array": <numpy.ndarray>,  # Full error map
    "pixels_per_degree": 67.0,        # Configuration used
    "flip_quality_description": "Moderate perceptual differences"
}
```

### Quality Descriptions

FLIP mean values map to quality descriptions:

| FLIP Mean | Description | Interpretation |
|-----------|-------------|----------------|
| < 0.01 | Imperceptible differences | Nearly identical to human eye |
| 0.01 - 0.05 | Just noticeable differences | Visible under close inspection |
| 0.05 - 0.10 | Slight perceptual differences | Noticeable but acceptable |
| 0.10 - 0.20 | Moderate perceptual differences | Clear differences visible |
| 0.20 - 0.50 | Noticeable perceptual differences | Significant quality impact |
| > 0.50 | Significant perceptual differences | Major visual discrepancies |

### Composite Scoring

When historical tracking is enabled, FLIP integrates into composite scores:

**Without FLIP (4-way split):**
```
Composite = 25% × pixel_diff + 25% × ssim + 25% × color + 25% × histogram
```

**With FLIP (5-way split):**
```
Composite = 20% × FLIP + 20% × pixel_diff + 20% × ssim + 20% × color + 20% × histogram
```

## Visualization Options

### FLIP Heatmaps

FLIP heatmaps visualize error distribution spatially:

- **Cool colors (blue/purple)**: Low perceptual error
- **Warm colors (yellow/red)**: High perceptual error

Heatmaps are:
1. Generated for each configured colormap
2. Saved as PNG files in the `diffs/` directory
3. Used as primary thumbnails in summary reports
4. Included in detail reports with tabbed colormap switching

### Report Features

Detail reports include:
- **Tabbed Colormap Interface**: Switch between colormaps interactively
- **4-Panel Comparison**: Known good, new, FLIP heatmap, metrics table
- **JavaScript Tab Switching**: Smooth colormap transitions
- **Base64 Embedded Images**: Self-contained HTML reports

### Thumbnail Selection

Summary reports automatically use FLIP heatmaps as thumbnails when enabled:

```
Priority: FLIP heatmap > Traditional diff image
```

This provides better visual indication of perceptual differences in overview pages.

## Integration with Historical Tracking

FLIP works seamlessly with historical metrics tracking:

```python
config = Config(
    base_dir="/project",
    new_dir="new",
    known_good_dir="baseline",
    enable_flip=True,
    enable_history=True,
    build_number="build_456",
    commit_hash="abc123def",  # Git commit for reproducibility
    anomaly_threshold=2.0      # σ for anomaly detection
)

comparator = ImageComparator(config)
results = list(comparator.compare_all_streaming())

# Historical data includes FLIP metrics
# Composite scores incorporate FLIP automatically
# Anomaly detection works with FLIP-enhanced composite scores
```

### Trend Analysis

Query historical FLIP data:

```python
from ImageComparisonSystem.history import Database, HistoryManager

db = Database(config.history_db_path)
history = HistoryManager(db)

# Get FLIP trend for specific image
trend = history.get_metric_trend("screenshot_001.png", "FLIP Perceptual Metric", "flip_mean")
for entry in trend:
    print(f"Build {entry.build_number}: FLIP mean = {entry.metric_value:.4f}")
```

## Performance Considerations

### Computational Cost

FLIP is more computationally expensive than traditional metrics:

| Metric | Relative Cost |
|--------|---------------|
| Pixel Difference | 1× (baseline) |
| SSIM | ~3× |
| **FLIP** | **~10-15×** |
| Histogram | ~2× |

### Optimization Strategies

1. **Opt-in by Default**: FLIP disabled unless explicitly enabled
2. **Parallel Processing**: Use `enable_parallel=True` for multiple images
3. **Selective Enablement**: Enable FLIP only for critical comparisons
4. **Caching**: FLIP error maps saved with results (avoid recomputation)

### Benchmark

Approximate processing times (100 images, 1920×1080):

| Configuration | Time |
|---------------|------|
| Without FLIP | ~2 minutes |
| With FLIP (sequential) | ~25 minutes |
| With FLIP (8 cores parallel) | ~4 minutes |

**Recommendation**: Always use parallel processing (`--enable-parallel`) when FLIP is enabled for large datasets.

## Troubleshooting

### FLIP Not Available

**Error**: `ImportError: NVIDIA FLIP not installed`

**Solution**:
```bash
pip install flip-evaluator>=1.0.0
```

### Invalid Colormap

**Error**: `ValueError: Invalid FLIP colormaps: {'invalid_name'}`

**Solution**: Use only valid colormaps:
```python
config.flip_colormaps = ["viridis", "jet", "turbo", "magma"]
```

### Default Colormap Not in List

**Error**: `ValueError: flip_default_colormap 'turbo' must be one of flip_colormaps: ['viridis']`

**Solution**: Ensure default is in the colormap list:
```python
config.flip_colormaps = ["viridis", "jet", "turbo"]
config.flip_default_colormap = "turbo"  # Now valid
```

### FLIP Section Not in Reports

**Check**:
1. FLIP is enabled: `config.enable_flip = True`
2. Visualization not disabled: `config.show_flip_visualization = True`
3. FLIP package installed: `python -c "import flip"`

### Grayscale Image Warning

FLIP expects RGB images. Grayscale images are automatically converted to RGB (3-channel) internally. This is normal and does not affect results.

### Performance Issues

If FLIP processing is too slow:

1. Enable parallel processing: `--enable-parallel`
2. Increase workers: `--max-workers 8`
3. Use for selective comparisons only
4. Consider higher `pixels_per_degree` for faster (less sensitive) analysis

## Best Practices

1. **Start with Defaults**: Use `flip_pixels_per_degree=67.0` initially
2. **Multiple Colormaps**: Generate 2-3 colormaps for different viewing preferences
3. **Enable History**: Track FLIP trends over time for quality regression detection
4. **Parallel Processing**: Always use for >10 images
5. **Documentation**: Record PPD value and viewing conditions in reports
6. **Validation**: Compare FLIP results with manual inspection initially
7. **Thresholds**: Establish project-specific FLIP mean thresholds for pass/fail

## References

- **NVIDIA FLIP Paper**: https://research.nvidia.com/publication/2020-07_FLIP
- **PyPI Package**: https://pypi.org/project/flip-evaluator/
- **Image Comparison Tool Docs**: See README.md

## Support

For issues or questions:
1. Check this guide first
2. Review example scripts in `examples/`
3. Run test suite: `pytest tests/test_flip*.py -v`
4. Submit issues: https://github.com/anthropics/ImageComparisonTool/issues
