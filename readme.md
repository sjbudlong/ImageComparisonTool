# Image Comparison Tool

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Offline Ready](https://img.shields.io/badge/offline-ready-green.svg)](QUICKSTART.md#for-offline-environments)

A modular Python system for comparing images and generating detailed HTML reports with visual diffs. Perfect for 3D rendering validation, visual regression testing, and quality assurance workflows.

## 🚀 Recent Enhancements (November 2025)

See [RECENT_CHANGES.md](RECENT_CHANGES.md) for detailed information about:
- ✨ **Recursive image discovery** - Compare images organized in nested subdirectories
- ✨ **Interactive metric descriptions** - Click ? icon to learn about metrics
- ✨ **Advanced histogram equalization** - CLAHE and LAB color space processing
- ✨ **Grayscale histogram visualization** - See both luminance and RGB distributions
- ✨ **Enhanced diff annotations** - Unenhanced diff as annotation target

## 🎯 Key Features

- **Automated Image Comparison**: Compare two sets of images and identify differences
  - **Recursive directory search**: Automatically finds images in nested subfolders
  - **Smart image matching**: Preserves directory structure with fallback filename matching
- **3D Space Optimization**: Advanced histogram equalization to normalize tonal variations while highlighting structural differences
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - LAB color space processing
  - Optional grayscale mode for maximum tonal normalization
- **Multiple Analysis Metrics**:
  - Pixel-level differences (percentage and count)
  - Structural Similarity Index (SSIM)
  - Color channel differences with thresholds
  - Dimension analysis
  - Histogram correlation and comparison
- **Visual Diff Generation**:
  - Adjustable contrast enhancement for difference images
  - Annotated images with bounding boxes showing difference areas
  - Configurable minimum contour area for noise reduction
- **Interactive HTML Reports**:
  - Click images to view full-size overlays with close button
  - Embedded grayscale and RGB channel histograms
  - Summary page sorted by difference percentage
  - Detailed metrics with interactive descriptions
  - Click ? icon next to metric headers to learn more
- **Flexible Configuration**:
  - GUI for easy setup with live color preview
  - Command-line interface for automation
  - Adjustable tolerances for all metrics
  - Customizable highlight colors and thresholds

## 📦 Installation

See [QUICKSTART.md](QUICKSTART.md) for quick setup, or read on for detailed instructions.

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Install (with internet)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Verify installation:
```bash
python dependencies.py
# or run full verification
python verify_installation.py
```

### Offline Installation

For systems without internet access, use the offline setup scripts:

#### Step 1: Prepare packages (on a machine WITH internet)

**Linux/Mac:**
```bash
chmod +x offline_setup.sh
./offline_setup.sh
```

**Windows:**
```batch
offline_setup.bat
```

This creates an `offline_packages/` directory containing all required Python packages.

#### Step 2: Transfer to offline machine

Copy the entire `offline_packages/` directory to your offline machine.

#### Step 3: Install on offline machine

**Linux/Mac:**
```bash
cd offline_packages
chmod +x install_offline.sh
./install_offline.sh
```

**Windows:**
```batch
cd offline_packages
install_offline.bat
```

#### Step 4: Verify installation

```bash
cd ..
python dependencies.py
python verify_installation.py
```

### Checking Dependencies

The system includes comprehensive dependency checking:

```bash
# Check all dependencies
python dependencies.py

# Check dependencies and save exact versions
python dependencies.py --save-freeze

# Run with dependency check
python main.py

# Skip dependency check (faster startup)
python main.py --skip-dependency-check

# Force dependency check and exit
python main.py --check-dependencies
```

### Troubleshooting Installation

**Missing tkinter (Linux):**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

**OpenCV issues:**
If you encounter OpenCV import errors, try:
```bash
pip uninstall opencv-python
pip install opencv-python-headless>=4.8.0
```

**Matplotlib backend issues:**
The system uses the 'Agg' backend (non-interactive) by default, which works in headless environments.

**Platform-specific wheel issues:**
If offline installation fails due to platform mismatches, re-download for your specific platform:
```bash
pip download <package> --platform manylinux2014_x86_64  # Linux
pip download <package> --platform win_amd64            # Windows
pip download <package> --platform macosx_10_9_x86_64   # macOS
```

## Usage

### GUI Mode (Interactive)

Simply run without arguments or use the `--gui` flag:

```bash
python main.py              # Default: launches GUI if no CLI args provided
python main.py --gui        # Explicitly request GUI mode
```

The GUI lets you:
- Select base directory
- Configure input/output folders
- Set difference thresholds
- Preview color selections
- Start comparison

### Command-Line Mode

The CLI supports flexible argument combinations - you only need to provide what you want to customize:

#### Minimal (uses smart defaults)
```bash
# Just specify base dir - uses 'new' and 'known_good' subdirs by default
python main.py --base-dir /path/to/project
```

#### Basic
```bash
python main.py \
  --base-dir /path/to/project \
  --new-dir new_images \
  --known-good-dir baseline_images
```

#### Full Options
```bash
python main.py \
  --base-dir /path/to/project \
  --new-dir new_images \
  --known-good-dir baseline_images \
  --diff-dir diffs \
  --html-dir reports \
  --pixel-diff-threshold 0.01 \
  --pixel-change-threshold 1 \
  --ssim-threshold 0.95 \
  --color-distance-threshold 10.0 \
  --min-contour-area 50 \
  --use-histogram-eq \
  --highlight-color "255,0,0" \
  --diff-enhancement 5.0 \
  --open-report
```

### CLI Arguments Reference

**Core Arguments:**
- `--base-dir`: Base directory for all operations (required for CLI mode)
- `--new-dir`: Subdirectory with new images (default: "new")
- `--known-good-dir`: Subdirectory with baseline images (default: "known_good")
- `--diff-dir`: Output subdirectory for diff images (default: "diffs")
- `--html-dir`: Output subdirectory for HTML reports (default: "reports")

**Tolerance Arguments:**
- `--pixel-diff-threshold`: Percentage threshold for flagging differences (default: 0.01)
- `--pixel-change-threshold`: Minimum pixel value change to count (default: 1)
- `--ssim-threshold`: SSIM similarity threshold 0-1 (default: 0.95)
- `--color-distance-threshold`: RGB color distance threshold (default: 10.0)
- `--min-contour-area`: Minimum area for bounding boxes in pixels (default: 50)

**Visual Arguments:**
- `--use-histogram-eq` / `--no-histogram-eq`: Enable/disable histogram equalization
- `--highlight-color`: RGB color for boxes, e.g., "255,0,0" for red (default: red)
- `--diff-enhancement`: Contrast enhancement factor, 1.0-10.0 (default: 5.0)

**Control Arguments:**
- `--open-report`: Auto-open summary report in browser after completion
- `--gui`: Force GUI mode even with other CLI args
- `--skip-dependency-check`: Skip dependency verification (faster)
- `--check-dependencies`: Check dependencies only and exit

## Directory Structure

```
base-dir/
├── new_images/           # New images to compare
│   ├── image1.png
│   └── image2.png
├── known_good/           # Baseline reference images
│   ├── image1.png
│   └── image2.png
├── diffs/               # Generated diff images
│   ├── diff_image1.png
│   └── annotated_image1.png
└── reports/             # HTML reports
    ├── summary.html
    ├── image1.png.html
    └── results.json
```

## Output

After running a comparison, you'll get:

1. **summary.html**: Overview of all comparisons, sorted by difference percentage
2. **Individual Reports**: One HTML page per image pair with:
   - Side-by-side image comparison
   - Enhanced difference visualization
   - Annotated differences with colored bounding boxes
   - Interactive histogram comparisons (RGB channels)
   - Detailed metrics and statistics
   - Clickable full-size image overlay with close button
3. **results.json**: Machine-readable results data

## Using Histogram Equalization for 3D Spaces

When comparing rendered 3D spaces, lighting and tonal variations can cause false positives. Histogram equalization normalizes these tonal differences while preserving structural changes:

**When to use:**
- Comparing 3D renders with different lighting
- Scenes with varying ambient conditions
- Testing geometry changes while ignoring illumination shifts

**How it works:**
- Redistributes pixel intensities to normalize tonal range
- Preserves structural and geometric differences
- Reduces false positives from lighting variations

**Configuration:**
- Enable in GUI: Check "Use Histogram Equalization"
- Enable in CLI: Add `--use-histogram-eq` flag
- Disable in CLI: Add `--no-histogram-eq` flag (default: enabled)

## Modular Architecture

### Core Components

- **main.py**: Entry point and argument parsing
- **config.py**: Configuration management
- **ui.py**: GUI interface using tkinter
- **comparator.py**: Orchestrates the comparison workflow
- **processor.py**: Image loading and diff generation
- **analyzers.py**: Modular analysis components
- **report_generator.py**: HTML report creation

### Adding Custom Analyzers

The system is designed to easily add new analysis metrics:

```python
from analyzers import ImageAnalyzer, AnalyzerRegistry

class MyCustomAnalyzer(ImageAnalyzer):
    @property
    def name(self) -> str:
        return "My Custom Metric"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> dict:
        # Your analysis logic here
        return {
            'custom_metric': some_calculation(img1, img2)
        }

# Register your analyzer
registry = AnalyzerRegistry()
registry.register(MyCustomAnalyzer())
```

### Supported Image Formats

- PNG
- JPEG/JPG
- BMP
- TIFF
- GIF

## Metrics Explained

### Pixel Difference
- **Percent Different**: Percentage of pixels that differ between images
- **Changed Pixels**: Absolute count of different pixels
- **Mean Absolute Error**: Average difference across all pixels
- **Max Difference**: Largest single pixel difference

### Structural Similarity (SSIM)
- **SSIM Score**: 0-1 scale, 1 = identical
- **SSIM Percentage**: Difference as percentage (100% - SSIM × 100)
- **Description**: Human-readable similarity level

### Color Difference
- **Per-Channel Differences**: RGB channel-specific analysis
- **Color Distance**: Euclidean distance in RGB space
- **Significant Changes**: Count of pixels exceeding threshold

### Histogram Analysis
- **Channel Correlation**: How similar the color distributions are (0-1 scale)
- **Chi-Square Distance**: Statistical measure of histogram differences
- **Visual Comparison**: Embedded histogram graphs in reports

### Dimensions
- **Size Comparison**: Width × Height for both images
- **Match Status**: Whether dimensions are identical

## Customizing Tolerances

All thresholds can be adjusted to suit your needs:

**Pixel Difference Threshold** (0.01%): Lower values catch subtle changes, higher values reduce noise
**Pixel Change Threshold** (1): Minimum pixel value change (0-255) to count as different
**SSIM Threshold** (0.95): Structural similarity requirement (0-1, higher = stricter)
**Color Distance Threshold** (10.0): RGB Euclidean distance for significant color changes
**Min Contour Area** (50 pixels): Filters out small noise when drawing bounding boxes

## Customizing Visual Output

**Highlight Color**: Change bounding box color
- Red: `255,0,0` (default)
- Blue: `0,0,255`
- Green: `0,255,0`
- Yellow: `255,255,0`
- Magenta: `255,0,255`

**Diff Enhancement**: Adjust contrast multiplication (1.0-10.0)
- 1.0 = No enhancement (raw difference)
- 5.0 = Default (good balance)
- 10.0 = Maximum contrast (very sensitive)

## Tips

1. **Organize Your Images**: Ensure matching filenames between new and known-good directories
2. **For 3D Renders**: Enable histogram equalization to ignore lighting variations
3. **Adjust Color Threshold**: For 3D spaces, increase `--color-distance-threshold` to 20-30 to ignore subtle shading differences
4. **Reduce Noise**: Increase `--min-contour-area` to 100-200 for cleaner bounding boxes on large images
5. **Custom Highlighting**: Use different colors for different test runs (e.g., blue for geometry changes, red for texture changes)
6. **Review Histograms**: Check histogram correlations to understand tonal shifts vs. structural changes
7. **Review Summary First**: Start with summary.html to see worst offenders
8. **Keyboard Navigation**: Press ESC to close full-size image overlays, or click the close button
9. **Automation**: Use CLI mode in CI/CD pipelines for automated visual regression testing
10. **Fine-tune SSIM**: Lower `--ssim-threshold` to 0.90 for more lenient comparisons, or raise to 0.98 for stricter matching

## License

MIT License - Feel free to use and modify as needed.
