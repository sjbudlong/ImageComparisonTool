# Image Comparison Tool - Setup Guide

## Quick Start

### 1. Install Dependencies

The tool requires Python 3.8+ and several dependencies. Install them using:

```bash
# Navigate to project directory
cd D:\GitRepos\ImageComparisonTool

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies:
- **Pillow** (>=8.0.0, <12.0.0) - Image processing
- **numpy** (>=1.19.0, <2.0.0) - Numerical computing
- **opencv-python** (>=4.5.0) - Computer vision
- **scikit-image** (>=0.19.0) - SSIM calculation
- **matplotlib** (>=3.3.0) - Histogram visualization

### 2. Verify Installation

```bash
python -c "import numpy, cv2, PIL, skimage, matplotlib; print('All dependencies installed!')"
```

### 3. Run the Tool

Basic usage:
```bash
cd ImageComparisonSystem
python main.py --base-dir path/to/your/images
```

With historical tracking:
```bash
python main.py --base-dir path/to/your/images --build-number "build-001"
```

## Common Issues

### ModuleNotFoundError: No module named 'numpy'

**Problem:** Dependencies not installed in current Python environment.

**Solution:**
```bash
pip install -r requirements.txt
```

### ImportError: attempted relative import with no known parent package

**Problem:** Running main.py from wrong directory or Python path issues.

**Solution:** Always run from the ImageComparisonSystem directory:
```bash
cd ImageComparisonSystem
python main.py --base-dir <path>
```

Or use the package module approach:
```bash
python -m ImageComparisonSystem.main --base-dir <path>
```

### Permission Denied Errors

**Problem:** Windows App Execution Aliases interfering with Python.

**Solution:**
1. Open Windows Settings → Apps → Apps & features → App execution aliases
2. Disable "App Installer" for python.exe and python3.exe
3. Or use full path to Python: `C:\Python39\python.exe -m pip install -r requirements.txt`

## Directory Structure

```
ImageComparisonTool/
├── ImageComparisonSystem/          # Main source code
│   ├── main.py                     # Entry point
│   ├── comparator.py               # Core comparison logic
│   ├── config.py                   # Configuration
│   ├── models.py                   # Data models
│   ├── analyzers.py                # Image analysis
│   ├── report_generator.py         # HTML report generation
│   ├── history/                    # Historical tracking
│   │   ├── database.py
│   │   ├── history_manager.py
│   │   ├── composite_metric.py
│   │   ├── statistics.py
│   │   └── retention.py
│   ├── annotations/                # ML annotation system
│   │   ├── annotation_manager.py
│   │   └── export_formats.py
│   └── visualization/              # Trend charts
│       └── trend_charts.py
├── tests/                          # Unit tests
├── requirements.txt                # Dependencies
└── README.md                       # Documentation
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database.py -v

# Run with coverage
pytest tests/ --cov=ImageComparisonSystem --cov-report=html
```

## Using Historical Tracking

### Enable History (Default)
```bash
python main.py --base-dir ./renders --build-number "build-1234"
```

### View Database Statistics
```bash
python main.py --base-dir ./renders --history-stats
```

### Cleanup Old Runs
```bash
# Dry run (preview)
python main.py --base-dir ./renders --cleanup-history --max-age-days 90 --dry-run

# Actually delete
python main.py --base-dir ./renders --cleanup-history --max-age-days 90
```

### Export Annotations
```bash
# Export in COCO format (default)
python main.py --base-dir ./renders --export-annotations

# Export in YOLO format
python main.py --base-dir ./renders --export-annotations --export-format yolo

# Export specific run
python main.py --base-dir ./renders --export-annotations --export-run-id 5
```

## Configuration Options

### Basic Options
- `--base-dir` - Base directory containing images (required)
- `--new-dir` - Directory with new images (default: base-dir)
- `--known-good-dir` - Directory with reference images (default: base-dir/known_good)
- `--output-dir` - Output directory for reports (default: base-dir/comparison_results)
- `--threshold` - Difference threshold percentage (default: 1.0)

### Historical Tracking Options
- `--build-number` - Build identifier for this run
- `--enable-history` / `--no-history` - Enable/disable historical tracking
- `--history-db` - Custom database path

### Retention/Cleanup Options
- `--cleanup-history` - Run retention policy cleanup
- `--max-runs` - Maximum number of runs to keep
- `--max-age-days` - Maximum age in days for runs
- `--dry-run` - Preview deletions without executing
- `--history-stats` - Display database statistics

### Annotation Export Options
- `--export-annotations` - Export annotations for ML training
- `--export-run-id` - Specify run ID to export (default: most recent)
- `--export-format` - Choose 'coco' or 'yolo' (default: coco)
- `--export-output` - Custom output path

### Performance Options
- `--parallel` - Enable parallel processing
- `--max-workers` - Maximum parallel workers (default: CPU count)

### Visual Options
- `--threshold-color` - RGB color for threshold highlighting (default: 255,0,0)
- `--highlight-color` - RGB color for difference highlighting (default: 255,255,0)
- `--enhancement-factor` - Difference enhancement factor (default: 5.0)

### Other Options
- `--open-report` - Automatically open report in browser
- `--log-level` - Set logging level (debug, info, warning, error, critical)
- `--log-file` - Path to log file

## Example Workflows

### First Time Setup and Comparison
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Navigate to source directory
cd ImageComparisonSystem

# 3. Run first comparison
python main.py --base-dir D:/MyProject/screenshots --build-number "baseline"
```

### Regular Comparison Run
```bash
python main.py \
  --base-dir D:/MyProject/screenshots \
  --build-number "build-2024-12-03-001" \
  --parallel \
  --open-report
```

### Review Historical Trends
```bash
# Check database stats
python main.py --base-dir D:/MyProject/screenshots --history-stats

# View reports in browser (generated in previous runs)
# Open: D:/MyProject/screenshots/comparison_results/summary.html
```

### Export Annotations for ML Training
```bash
# Export recent annotations in COCO format
python main.py --base-dir D:/MyProject/screenshots --export-annotations

# Export specific run in YOLO format
python main.py \
  --base-dir D:/MyProject/screenshots \
  --export-annotations \
  --export-run-id 5 \
  --export-format yolo \
  --export-output ./ml_training/labels
```

### Cleanup Old Data
```bash
# Preview what would be deleted (runs older than 60 days)
python main.py \
  --base-dir D:/MyProject/screenshots \
  --cleanup-history \
  --max-age-days 60 \
  --dry-run

# Actually delete (keeps annotated and anomalous runs)
python main.py \
  --base-dir D:/MyProject/screenshots \
  --cleanup-history \
  --max-age-days 60
```

## Troubleshooting

### Images Not Found
- Verify `--base-dir` points to correct location
- Check that `known_good` subdirectory exists
- Ensure image files have matching names in both directories

### No Differences Detected
- Check `--threshold` setting (try lower value like 0.1)
- Verify images are actually different
- Check image format compatibility

### Performance Issues
- Enable `--parallel` for faster processing
- Reduce `--max-workers` if system runs out of memory
- Consider using `--cleanup-history` to reduce database size

### Database Errors
- Check database file permissions
- Verify disk space available
- Check `.imgcomp_history` directory exists and is writable

### Import Errors
- Verify all dependencies installed: `pip list | grep -E "numpy|opencv|Pillow|scikit-image|matplotlib"`
- Try reinstalling: `pip install --force-reinstall -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)

## Getting Help

- Check [README.md](../README.md) for feature documentation
- Review [HISTORICAL_TRACKING_COMPLETE.md](HISTORICAL_TRACKING_COMPLETE.md) for historical features
- Run with `--help` for all options: `python main.py --help`
- Enable debug logging: `python main.py --log-level debug --base-dir <path>`
