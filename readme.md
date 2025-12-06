# Image Comparison Tool

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Offline Ready](https://img.shields.io/badge/offline-ready-green.svg)](SETUP_GUIDE.md#for-offline-environments)

A comprehensive Python system for comparing images with **historical metrics tracking**, **NVIDIA FLIP perceptual analysis**, **ML annotation support**, and **advanced visual regression testing**. Perfect for 3D rendering validation, VFX quality assurance, automated testing pipelines, and enterprise QA workflows.

## 🎉 Major Updates

### NVIDIA FLIP Perceptual Metric (Latest)

**Optional perceptual image comparison** that models human visual perception:

- 👁️ **Human Visual System (HVS) Modeling** - Detects differences as humans actually see them
- 🎨 **Perceptual Quality Scoring** - Superior to SSIM for rendering, VFX, and gaming QA
- 🔥 **Interactive Heatmap Visualizations** - Multiple colormaps (viridis, jet, turbo, magma)
- ⚙️ **Configurable Viewing Distance** - Adjust pixels-per-degree for your use case
- 📊 **Integrated with Historical Tracking** - FLIP metrics included in composite scoring
- 🚀 **Opt-in Design** - Disabled by default for performance, enable when needed

**Installation:** `pip install flip-image-comparison` (optional)
**Usage:** Add `--enable-flip` flag or check GUI option
**Documentation:** See [FLIP_INTEGRATION_GUIDE.md](FLIP_INTEGRATION_GUIDE.md)

### Historical Metrics Tracking (December 2025)

**All 12 phases complete!** Enterprise-grade historical tracking capabilities:

- 📊 **Historical Metrics Database** - SQLite-based tracking of all comparison runs over time
- 📈 **Composite Scoring** - Weighted combination of multiple metrics with configurable weights
- 🚨 **Statistical Anomaly Detection** - Automatic flagging of results >2σ from historical mean
- 📉 **Trend Visualization** - Interactive charts showing metric evolution over time
- 🏷️ **ML Annotation System** - Full CRUD for training data annotations (bounding box, polygon, point, classification)
- 🤖 **ML Export Formats** - Export annotations in COCO and YOLO formats for model training
- 🗄️ **Smart Data Retention** - Configurable cleanup policies that preserve important data
- 🔍 **Database Analytics** - Query historical trends, compare runs, analyze anomalies

See [HISTORICAL_TRACKING_COMPLETE.md](HISTORICAL_TRACKING_COMPLETE.md) for complete documentation.

### Recent Enhancements

See [RECENT_CHANGES.md](RECENT_CHANGES.md) for detailed information about:
- ✨ **Recursive image discovery** - Compare images organized in nested subdirectories
- ✨ **Interactive metric descriptions** - Click ? icon to learn about metrics
- ✨ **Advanced histogram equalization** - CLAHE and LAB color space processing
- ✨ **Grayscale histogram visualization** - See both luminance and RGB distributions
- ✨ **Enhanced diff annotations** - Unenhanced diff as annotation target
- ✨ **Markdown report exporter** - CI/CD pipeline integration (Azure DevOps, GitHub Actions)

## 🎯 Key Features

### Core Comparison Engine
- **Automated Image Comparison**: Compare two sets of images and identify differences
  - **Recursive directory search**: Automatically finds images in nested subfolders
  - **Smart image matching**: Preserves directory structure with fallback filename matching
  - **Parallel processing**: Multi-core support for processing thousands of images
- **3D Space Optimization**: Advanced histogram equalization to normalize tonal variations
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - LAB color space processing
  - Optional grayscale mode for maximum tonal normalization

### Metrics & Analysis
- **Multiple Analysis Metrics**:
  - **NVIDIA FLIP** - Perceptual metric modeling human vision (optional)
  - Pixel-level differences (percentage and count)
  - Structural Similarity Index (SSIM)
  - Color channel differences with thresholds
  - Dimension analysis
  - Histogram correlation and comparison
- **Composite Metrics**: Weighted combination of all metrics into single score
  - 4-way split without FLIP (25% each: pixel, SSIM, color, histogram)
  - 5-way split with FLIP (20% each: FLIP, pixel, SSIM, color, histogram)
- **Historical Statistics**: Mean, standard deviation, deviation from baseline
- **Anomaly Detection**: Statistical flagging of outliers (>2σ threshold)

### Visual Output & Reporting
- **Visual Diff Generation**:
  - Adjustable contrast enhancement for difference images
  - Annotated images with bounding boxes showing difference areas
  - **FLIP heatmaps** with multiple colormaps for perceptual difference visualization
  - Configurable minimum contour area for noise reduction
- **Interactive HTML Reports**:
  - Click images to view full-size overlays
  - **FLIP perceptual analysis section** with tabbed colormap switching
  - Embedded grayscale and RGB channel histograms
  - **Historical trend charts** showing composite scores over time
  - **Anomaly badges** highlighting statistical outliers
  - Summary pages with composite score sorting
  - Detailed metrics with interactive descriptions
- **CI/CD Pipeline Integration**:
  - Markdown summary reports (`summary.md`) for build pipelines
  - Machine-readable JSON format
  - Comprehensive statistics and status categorization

### Historical Tracking & ML Features
- **Database Persistence**: SQLite database tracking all runs (one DB per project)
- **Build Identification**: Track runs by build number or identifier
- **Trend Analysis**: Compare current results against historical baselines
- **Annotation System**: Add bounding boxes, polygons, points, or classifications to results
- **ML Training Export**: Export annotations in COCO or YOLO format
- **Data Retention**: Configurable policies with smart protection for annotated/anomalous data
- **Query & Analytics**: Search annotations by label/category, generate statistics

### Flexible Configuration
- **GUI Mode**: Easy setup with live color preview, histogram controls, and FLIP configuration
- **Command-line Interface**: Full automation support with 40+ arguments
- **Configurable Weights**: Adjust composite metric formula per project
- **Adjustable Tolerances**: Fine-tune all thresholds for your use case

## 📦 Installation

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for comprehensive setup instructions, or use the quick start below.

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Install

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Verify installation:
```bash
python -c "import numpy, cv2, PIL, skimage, matplotlib, flip; print('All dependencies installed!')"
```

3. Run your first comparison:
```bash
cd ImageComparisonSystem
python main.py --base-dir path/to/your/images --build-number "baseline"
```

### Required Dependencies

- **Pillow** (>=8.0.0) - Image processing
- **numpy** (>=1.19.0) - Numerical computing
- **opencv-python** (>=4.5.0) - Computer vision
- **scikit-image** (>=0.19.0) - SSIM calculation
- **matplotlib** (>=3.3.0) - Histogram and trend visualization
- **flip-evaluator** (>=1.0.0) - NVIDIA FLIP perceptual metric

See [requirements.txt](requirements.txt) for complete list.

## 📖 Usage

### Basic Comparison (No History)

```bash
cd ImageComparisonSystem
python main.py --base-dir /path/to/images
```

### Comparison with Historical Tracking (Recommended)

```bash
cd ImageComparisonSystem
python main.py --base-dir /path/to/images --build-number "build-2025-12-03-001"
```

This will:
- Compare all images in `new/` against `known_good/`
- Store results in SQLite database (`.imgcomp_history/comparison_history.db`)
- Calculate composite scores and detect anomalies
- Generate HTML reports with historical trend charts
- Preserve data for future comparisons

### Using NVIDIA FLIP Perceptual Analysis

```bash
# Enable FLIP with default settings
python main.py --base-dir /path/to/images --enable-flip

# Enable FLIP with custom viewing distance and colormaps
python main.py --base-dir /path/to/images --enable-flip \
  --flip-pixels-per-degree 42.0 \
  --flip-colormaps viridis jet turbo
```

See [FLIP_INTEGRATION_GUIDE.md](FLIP_INTEGRATION_GUIDE.md) for comprehensive FLIP documentation.

### Historical Tracking Features

#### View Database Statistics
```bash
python main.py --base-dir /path/to/images --history-stats
```

#### Cleanup Old Runs
```bash
# Preview what would be deleted
python main.py --base-dir /path/to/images --cleanup-history --max-age-days 90 --dry-run

# Actually delete old runs (preserves annotated and anomalous data)
python main.py --base-dir /path/to/images --cleanup-history --max-age-days 90
```

#### Export Annotations for ML Training
```bash
# Export in COCO format (default)
python main.py --base-dir /path/to/images --export-annotations

# Export in YOLO format
python main.py --base-dir /path/to/images --export-annotations --export-format yolo

# Export specific run
python main.py --base-dir /path/to/images --export-annotations --export-run-id 5
```

### GUI Mode (Interactive)

```bash
python main.py --gui
```

The GUI provides:
- Visual configuration of all settings
- Color picker with live preview
- Histogram visualization controls
- **NVIDIA FLIP configuration section** (pixels per degree, colormaps)
- One-click comparison start

### Command-Line Options

#### Core Arguments
- `--base-dir` - Base directory (required)
- `--new-dir` - New images subdirectory (default: "new")
- `--known-good-dir` - Baseline images subdirectory (default: "known_good")
- `--output-dir` - Output directory (default: "comparison_results")

#### FLIP Arguments (Optional)
- `--enable-flip` - Enable NVIDIA FLIP perceptual analysis
- `--flip-pixels-per-degree` - Viewing distance parameter (default: 67.0)
- `--flip-colormaps` - Heatmap colormaps (default: viridis; options: viridis, jet, turbo, magma)
- `--flip-default-colormap` - Primary colormap for reports (default: viridis)

#### Historical Tracking Arguments
- `--build-number` - Build identifier for this run
- `--enable-history` / `--no-history` - Enable/disable historical tracking (default: enabled)
- `--history-db` - Custom database path

#### Retention/Cleanup Arguments
- `--cleanup-history` - Run retention policy cleanup
- `--max-runs` - Maximum number of runs to keep
- `--max-age-days` - Maximum age in days for runs
- `--dry-run` - Preview deletions without executing
- `--history-stats` - Display database statistics

#### Annotation Export Arguments
- `--export-annotations` - Export annotations for ML training
- `--export-run-id` - Specify run ID (default: most recent)
- `--export-format` - Choose 'coco' or 'yolo' (default: coco)
- `--export-output` - Custom output path

#### Tolerance Arguments
- `--pixel-diff-threshold` - Pixel difference percentage (default: 0.01)
- `--ssim-threshold` - SSIM threshold 0-1 (default: 0.95)
- `--color-distance-threshold` - RGB distance threshold (default: 10.0)
- `--min-contour-area` - Minimum bounding box area (default: 50)

#### Performance Arguments
- `--parallel` - Enable parallel processing
- `--max-workers` - Maximum parallel workers (default: CPU count)

#### Visual Arguments
- `--use-histogram-eq` / `--no-histogram-eq` - Histogram equalization
- `--highlight-color` - RGB color for boxes (default: "255,0,0")
- `--diff-enhancement` - Contrast enhancement factor (default: 5.0)

#### Control Arguments
- `--open-report` - Auto-open summary report in browser
- `--log-level` - Logging level (debug, info, warning, error, critical)
- `--log-file` - Path to log file

Run `python main.py --help` for complete argument list.

## 🏗️ Architecture

### Module Structure

```
ImageComparisonSystem/
├── main.py                          # Entry point & CLI argument parsing
├── config.py                        # Configuration management (FLIP settings included)
├── models.py                        # Data models (ComparisonResult with history fields)
├── comparator.py                    # Main comparison orchestration (FLIP integration)
├── processor.py                     # Image loading, diff generation, FLIP heatmaps
├── analyzers.py                     # Modular analysis components (FLIP analyzer)
├── report_generator.py              # HTML report creation (FLIP sections, trend charts)
├── ui.py                            # GUI interface (FLIP controls)
│
├── history/                         # Historical Tracking System
│   ├── __init__.py
│   ├── database.py                  # SQLite schema & connection management
│   ├── history_manager.py           # CRUD operations for runs/results
│   ├── composite_metric.py          # Weighted metric calculator (FLIP support)
│   ├── statistics.py                # Statistical analysis & anomaly detection
│   ├── retention.py                 # Data cleanup policies
│   └── migrations/
│       └── v1_initial_schema.sql    # Database schema definition
│
├── annotations/                     # ML Annotation System
│   ├── __init__.py
│   ├── annotation_manager.py        # CRUD for annotations
│   └── export_formats.py            # COCO/YOLO exporters
│
└── visualization/                   # Data Visualization
    ├── __init__.py
    └── trend_charts.py              # Matplotlib-based trend charts
```

### Database Schema

#### Core Tables
- **runs** - Comparison run metadata (build_number, timestamp, config, totals)
- **results** - Per-image comparison results with all metrics (FLIP metrics included)
- **annotations** - ML training annotations (geometry, labels, categories)
- **composite_metric_config** - Metric weight configuration (FLIP weights)
- **retention_policy** - Data cleanup settings

#### Key Relationships
- runs 1:N results (CASCADE DELETE)
- results 1:N annotations (CASCADE DELETE)
- Separate database per project (located at `<base-dir>/.imgcomp_history/comparison_history.db`)

### Data Flow

```
1. Image Comparison
   ├─> Load & analyze images (processor.py, analyzers.py)
   ├─> Calculate FLIP error map (optional, analyzers.py)
   ├─> Generate FLIP heatmaps (processor.py)
   ├─> Calculate composite score (composite_metric.py with FLIP)
   ├─> Query historical data (history_manager.py)
   ├─> Detect anomalies (statistics.py)
   └─> Save to database (database.py)

2. Report Generation
   ├─> Generate FLIP heatmap tabs (report_generator.py)
   ├─> Generate trend charts (trend_charts.py)
   ├─> Create HTML reports (report_generator.py)
   └─> Export for CI/CD (Markdown, JSON)

3. Annotation Workflow
   ├─> Add annotations via API (annotation_manager.py)
   ├─> Query by label/category
   ├─> Export to COCO/YOLO (export_formats.py)
   └─> Use for ML training

4. Data Management
   ├─> Apply retention policies (retention.py)
   ├─> Protect annotated/anomalous runs
   └─> Maintain optimal database size
```

## 📊 Metrics Explained

### Core Metrics (Individual)
- **NVIDIA FLIP** - Perceptual error (0-1 scale, 0=imperceptible, 1=significant)
- **Pixel Difference** - Percentage of changed pixels
- **SSIM (Structural Similarity)** - 0-1 score measuring structural likeness
- **Color Distance** - Euclidean distance in RGB space
- **Histogram Correlation** - Distribution similarity (0-1)

### Composite Metric (Historical)
Weighted combination of all metrics, normalized to 0-100 scale:

**Without FLIP (4-way split):**
```python
composite_score = (
    0.25 * normalize(pixel_diff) +
    0.25 * normalize(1 - ssim) +
    0.25 * normalize(color_distance) +
    0.25 * normalize(histogram_chi_square)
) * 100
```

**With FLIP (5-way split):**
```python
composite_score = (
    0.20 * normalize(flip_mean) +
    0.20 * normalize(pixel_diff) +
    0.20 * normalize(1 - ssim) +
    0.20 * normalize(color_distance) +
    0.20 * normalize(histogram_chi_square)
) * 100
```

**Default weights**: Equal weighting (auto-adjusts based on FLIP availability)
**Configurable**: Adjust weights per project in database or via `composite_metric_weights` config parameter

### FLIP Quality Descriptions

| FLIP Mean | Description | Interpretation |
|-----------|-------------|----------------|
| < 0.01 | Imperceptible differences | Nearly identical to human eye |
| 0.01 - 0.05 | Just noticeable differences | Visible under close inspection |
| 0.05 - 0.10 | Slight perceptual differences | Noticeable but acceptable |
| 0.10 - 0.20 | Moderate perceptual differences | Clear differences visible |
| 0.20 - 0.50 | Noticeable perceptual differences | Significant quality impact |
| > 0.50 | Significant perceptual differences | Major visual discrepancies |

### Statistical Metrics (Historical)
- **Historical Mean** - Average composite score across all runs
- **Standard Deviation** - Measure of score variability
- **Deviation from Mean** - Current score's σ distance from mean
- **Anomaly Flag** - Automatic flagging if |deviation| > 2σ

## 🎨 Output

### HTML Reports

After comparison, you get:

1. **summary.html** - Overview sorted by composite score
   - Table with avg/max differences per subdirectory
   - Composite score column
   - Anomaly count badges
   - **FLIP heatmap thumbnails** (when FLIP enabled)

2. **Individual Detail Pages** - One per image pair
   - Side-by-side comparison
   - Enhanced difference visualization
   - **FLIP perceptual analysis section** with tabbed colormaps (when enabled)
   - Annotated differences with bounding boxes
   - **Historical trend chart** showing composite scores over time
   - **Statistical analysis section** (mean, std dev, deviation)
   - **Anomaly warning badges** for outliers
   - Interactive histograms (RGB + grayscale)
   - Full metrics breakdown

3. **summary.md** - Markdown for CI/CD pipelines
   - Build status summary
   - Categorized results (passing, warning, critical)
   - Statistics table
   - ISO timestamps

4. **results.json** - Machine-readable data

### Database Exports

- **COCO Format** - JSON with images, annotations, categories (for Detectron2, MMDetection, etc.)
- **YOLO Format** - Text files with normalized coordinates + classes.txt (for YOLO models)

## 🔬 Example Workflows

### VFX Rendering Quality Assurance with FLIP

```bash
# Compare renders with perceptual analysis
python main.py \
  --base-dir ./vfx_renders \
  --build-number "shot_042_v3" \
  --enable-flip \
  --flip-pixels-per-degree 42.0 \
  --flip-colormaps viridis turbo \
  --parallel \
  --max-workers 8

# Check for perceptual anomalies
python -c "
import json
data = json.load(open('./vfx_renders/comparison_results/results.json'))
flip_issues = [r for r in data['results'] if r.get('metrics', {}).get('FLIP Perceptual Metric', {}).get('flip_mean', 0) > 0.15]
exit(1 if flip_issues else 0)
"
```

### Continuous Integration Testing

```bash
# Jenkins/GitHub Actions/Azure DevOps
python main.py \
  --base-dir ./test_renders \
  --build-number "$BUILD_ID" \
  --parallel \
  --max-workers 8 \
  --log-file ci_log.txt

# Check for anomalies (exit code 1 if any found)
python -c "import json; data=json.load(open('test_renders/comparison_results/results.json')); exit(1 if any(r.get('is_anomaly') for r in data.get('results', [])) else 0)"
```

### ML Model Training Preparation

```bash
# 1. Run comparison with history
python main.py --base-dir ./renders --build-number "v1.0"

# 2. Manually annotate anomalies (via programmatic API or future UI)
# ... add annotations to database ...

# 3. Export annotations for training
python main.py --base-dir ./renders --export-annotations --export-format coco

# 4. Train your model
# python train.py --data ./renders/.imgcomp_history/exports/annotations_run_*.json
```

### Regression Testing Over Time

```bash
# Week 1: Establish baseline
python main.py --base-dir ./renders --build-number "baseline-001"

# Week 2-N: Compare against baseline
python main.py --base-dir ./renders --build-number "build-$(date +%Y%m%d)"

# Review trends
python main.py --base-dir ./renders --history-stats

# Cleanup old data quarterly
python main.py --base-dir ./renders --cleanup-history --max-age-days 90
```

## 🛠️ Customization

### Adding Custom Analyzers

```python
from analyzers import ImageAnalyzer, AnalyzerRegistry
import numpy as np

class MyCustomAnalyzer(ImageAnalyzer):
    @property
    def name(self) -> str:
        return "My Custom Metric"

    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> dict:
        # Your analysis logic here
        custom_value = np.mean(np.abs(img1 - img2))
        return {
            'custom_metric': float(custom_value),
            'description': f"Custom value: {custom_value:.2f}"
        }

# Register analyzer
registry = AnalyzerRegistry()
registry.register(MyCustomAnalyzer())
```

### Adjusting Composite Metric Weights

```python
from history import Database, CompositeMetricCalculator

# With FLIP (5-way split)
calculator = CompositeMetricCalculator(weights={
    "flip": 0.40,               # Emphasize FLIP
    "pixel_diff": 0.15,
    "ssim": 0.15,
    "color_distance": 0.15,
    "histogram": 0.15
})

# Without FLIP (4-way split)
calculator = CompositeMetricCalculator(weights={
    "pixel_diff": 0.4,          # Emphasize pixel differences
    "ssim": 0.3,
    "color_distance": 0.2,
    "histogram": 0.1
})
```

### Programmatic Annotation API

```python
from history import Database
from annotations import AnnotationManager

db = Database(".imgcomp_history/comparison_history.db")
manager = AnnotationManager(db)

# Add bounding box annotation
ann_id = manager.add_annotation(
    result_id=123,
    annotation_type="bounding_box",
    geometry={"x": 100, "y": 200, "width": 150, "height": 100},
    label="rendering_artifact",
    category="geometry_issues",
    annotator_name="qa_team",
    notes="Shadow rendering incorrect"
)

# Query annotations
artifacts = manager.get_annotations_by_label("rendering_artifact")
stats = manager.get_annotation_statistics()
```

## 💡 Tips & Best Practices

### General
1. **Organize Images**: Use consistent filenames between `new/` and `known_good/` directories
2. **For 3D Renders**: Enable histogram equalization to normalize lighting variations
3. **Review Summary First**: Start with summary.html to identify worst offenders
4. **Use Build Numbers**: Always specify `--build-number` to enable historical tracking

### FLIP Usage
5. **Start with Defaults**: Use default pixels_per_degree (67.0) initially
6. **Multiple Colormaps**: Generate 2-3 colormaps for different viewing preferences
7. **Enable for Critical QA**: Use FLIP for rendering validation, VFX, and visual quality testing
8. **Parallel Processing with FLIP**: Always use `--parallel` when FLIP is enabled for large datasets

### Performance
9. **Enable Parallel Processing**: Use `--parallel` for 100+ images
10. **SSD Storage**: Keep databases on SSD for faster query performance
11. **Cleanup Regularly**: Run retention policies quarterly to maintain optimal database size

### Historical Tracking
12. **Consistent Builds**: Use structured build numbers (e.g., "YYYY-MM-DD-###") for easy sorting
13. **Annotate Anomalies**: Mark statistical outliers with annotations for future reference
14. **Monitor Trends**: Check `--history-stats` periodically to understand metric drift

### ML Training
15. **Diverse Annotations**: Include multiple geometry types (bbox, polygon, point) for robust training
16. **Label Consistency**: Use standardized labels and categories across all annotations
17. **Export Regularly**: Export annotations after each annotation session to prevent data loss

### Configuration
18. **Fine-tune SSIM**: Lower to 0.90 for lenient comparisons, raise to 0.98 for strict matching
19. **Adjust Color Threshold**: For 3D scenes, increase to 20-30 to ignore subtle shading
20. **Custom Weights**: Tailor composite metric weights to emphasize metrics important to your project

## 📚 Documentation

- **[README.md](README.md)** - This file (overview)
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Installation and troubleshooting
- **[FLIP_INTEGRATION_GUIDE.md](FLIP_INTEGRATION_GUIDE.md)** - Complete NVIDIA FLIP documentation
- **[HISTORICAL_TRACKING_COMPLETE.md](HISTORICAL_TRACKING_COMPLETE.md)** - Complete historical features guide
- **[RECENT_CHANGES.md](RECENT_CHANGES.md)** - Recent feature additions

### Inline Documentation
- All modules have comprehensive docstrings
- Example usage in class/function docstrings
- Type hints throughout codebase

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ImageComparisonSystem --cov-report=html

# Run specific test suites
pytest tests/test_database.py -v
pytest tests/test_annotation_manager.py -v
pytest tests/test_export_formats.py -v
pytest tests/test_flip*.py -v
```

**Test Coverage**: 140+ unit tests across all modules (including FLIP integration tests)

## 🤝 Contributing

Contributions welcome! The codebase is designed for easy extension:

- **Analyzers**: Add new metrics via `AnalyzerRegistry`
- **Exporters**: Add new annotation formats in `export_formats.py`
- **Visualizations**: Extend `TrendChartGenerator` with new chart types
- **Retention Policies**: Customize cleanup logic in `retention.py`

## 📄 License

MIT License - Feel free to use and modify as needed.

## 🙏 Acknowledgments

Built with:
- **Pillow** - Image processing
- **OpenCV** - Computer vision
- **scikit-image** - SSIM calculation
- **matplotlib** - Visualization
- **numpy** - Numerical computing
- **SQLite** - Database persistence
- **NVIDIA FLIP** - Perceptual image comparison (optional)

---

**For support, bug reports, or feature requests**, please check existing documentation or create an issue in your repository.
