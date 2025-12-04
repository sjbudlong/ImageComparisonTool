# Image Comparison Tool

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Offline Ready](https://img.shields.io/badge/offline-ready-green.svg)](QUICKSTART.md#for-offline-environments)

A comprehensive Python system for comparing images with **historical metrics tracking**, **ML annotation support**, and **advanced visual regression testing**. Perfect for 3D rendering validation, automated testing pipelines, and quality assurance workflows.

## 🎉 Major Update: Historical Metrics Tracking (December 2025)

**All 12 phases complete!** The system now includes enterprise-grade historical tracking capabilities:

### New Capabilities
- 📊 **Historical Metrics Database** - SQLite-based tracking of all comparison runs over time
- 📈 **Composite Scoring** - Weighted combination of multiple metrics with configurable weights
- 🚨 **Statistical Anomaly Detection** - Automatic flagging of results >2σ from historical mean
- 📉 **Trend Visualization** - Interactive charts showing metric evolution over time
- 🏷️ **ML Annotation System** - Full CRUD for training data annotations (bounding box, polygon, point, classification)
- 🤖 **ML Export Formats** - Export annotations in COCO and YOLO formats for model training
- 🗄️ **Smart Data Retention** - Configurable cleanup policies that preserve important data
- 🔍 **Database Analytics** - Query historical trends, compare runs, analyze anomalies

See [HISTORICAL_TRACKING_COMPLETE.md](HISTORICAL_TRACKING_COMPLETE.md) for complete documentation.

## 🚀 Recent Enhancements

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
  - Pixel-level differences (percentage and count)
  - Structural Similarity Index (SSIM)
  - Color channel differences with thresholds
  - Dimension analysis
  - Histogram correlation and comparison
- **Composite Metrics**: Weighted combination of all metrics into single score
- **Historical Statistics**: Mean, standard deviation, deviation from baseline
- **Anomaly Detection**: Statistical flagging of outliers (>2σ threshold)

### Visual Output & Reporting
- **Visual Diff Generation**:
  - Adjustable contrast enhancement for difference images
  - Annotated images with bounding boxes showing difference areas
  - Configurable minimum contour area for noise reduction
- **Interactive HTML Reports**:
  - Click images to view full-size overlays
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
- **GUI Mode**: Easy setup with live color preview and histogram controls
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
python -c "import numpy, cv2, PIL, skimage, matplotlib; print('All dependencies installed!')"
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
- One-click comparison start

### Command-Line Options

#### Core Arguments
- `--base-dir` - Base directory (required)
- `--new-dir` - New images subdirectory (default: "new")
- `--known-good-dir` - Baseline images subdirectory (default: "known_good")
- `--output-dir` - Output directory (default: "comparison_results")

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
├── config.py                        # Configuration management
├── models.py                        # Data models (ComparisonResult with history fields)
├── comparator.py                    # Main comparison orchestration
├── processor.py                     # Image loading & diff generation
├── analyzers.py                     # Modular analysis components
├── report_generator.py              # HTML report creation with trend charts
├── ui.py                            # GUI interface
│
├── history/                         # Historical Tracking System
│   ├── __init__.py
│   ├── database.py                  # SQLite schema & connection management
│   ├── history_manager.py           # CRUD operations for runs/results
│   ├── composite_metric.py          # Weighted metric calculator
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
- **results** - Per-image comparison results with all metrics
- **annotations** - ML training annotations (geometry, labels, categories)
- **composite_metric_config** - Metric weight configuration
- **retention_policy** - Data cleanup settings

#### Key Relationships
- runs 1:N results (CASCADE DELETE)
- results 1:N annotations (CASCADE DELETE)
- Separate database per project (located at `<base-dir>/.imgcomp_history/comparison_history.db`)

### Data Flow

```
1. Image Comparison
   ├─> Load & analyze images (processor.py, analyzers.py)
   ├─> Calculate composite score (composite_metric.py)
   ├─> Query historical data (history_manager.py)
   ├─> Detect anomalies (statistics.py)
   └─> Save to database (database.py)

2. Report Generation
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
- **Pixel Difference** - Percentage of changed pixels
- **SSIM (Structural Similarity)** - 0-1 score measuring structural likeness
- **Color Distance** - Euclidean distance in RGB space
- **Histogram Correlation** - Distribution similarity (0-1)

### Composite Metric (Historical)
Weighted combination of all metrics, normalized to 0-100 scale:

```python
composite_score = (
    w1 * normalize(pixel_diff) +
    w2 * normalize(1 - ssim) +
    w3 * normalize(color_distance) +
    w4 * normalize(histogram_chi_square)
) * 100
```

**Default weights**: 0.25 each (equal weighting)
**Configurable**: Adjust weights per project in database

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
   - **New:** Composite score column
   - **New:** Anomaly count badges
   - Thumbnail grid with difference percentages

2. **Individual Detail Pages** - One per image pair
   - Side-by-side comparison
   - Enhanced difference visualization
   - Annotated differences with bounding boxes
   - **New:** Historical trend chart showing composite scores over time
   - **New:** Statistical analysis section (mean, std dev, deviation)
   - **New:** Anomaly warning badges for outliers
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

db = Database("comparison_history.db")
calculator = CompositeMetricCalculator(db)

# Update weights (must sum to 1.0)
calculator.update_config_weights({
    "weight_pixel_diff": 0.4,      # Emphasize pixel differences
    "weight_ssim": 0.3,
    "weight_color_distance": 0.2,
    "weight_histogram": 0.1
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

### Performance
5. **Enable Parallel Processing**: Use `--parallel` for 100+ images
6. **SSD Storage**: Keep databases on SSD for faster query performance
7. **Cleanup Regularly**: Run retention policies quarterly to maintain optimal database size

### Historical Tracking
8. **Consistent Builds**: Use structured build numbers (e.g., "YYYY-MM-DD-###") for easy sorting
9. **Annotate Anomalies**: Mark statistical outliers with annotations for future reference
10. **Monitor Trends**: Check `--history-stats` periodically to understand metric drift

### ML Training
11. **Diverse Annotations**: Include multiple geometry types (bbox, polygon, point) for robust training
12. **Label Consistency**: Use standardized labels and categories across all annotations
13. **Export Regularly**: Export annotations after each annotation session to prevent data loss

### Configuration
14. **Fine-tune SSIM**: Lower to 0.90 for lenient comparisons, raise to 0.98 for strict matching
15. **Adjust Color Threshold**: For 3D scenes, increase to 20-30 to ignore subtle shading
16. **Custom Weights**: Tailor composite metric weights to emphasize metrics important to your project

## 📚 Documentation

- **[README.md](README.md)** - This file (overview)
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Installation and troubleshooting
- **[HISTORICAL_TRACKING_COMPLETE.md](HISTORICAL_TRACKING_COMPLETE.md)** - Complete historical features guide
- **[RECENT_CHANGES.md](RECENT_CHANGES.md)** - Recent feature additions
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup for offline environments

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
```

**Test Coverage**: 127+ unit tests across all modules

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

---

**For support, bug reports, or feature requests**, please check existing documentation or create an issue in your repository.
