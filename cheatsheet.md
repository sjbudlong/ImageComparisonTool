# Image Comparison Tool - Quick Reference

## Installation Commands

```bash
# Online installation
pip install -r requirements.txt

# Offline preparation (on internet machine)
./offline_setup.sh              # Linux/Mac
offline_setup.bat               # Windows

# Offline installation (on offline machine)
cd offline_packages
./install_offline.sh            # Linux/Mac
install_offline.bat             # Windows

# Install as package
pip install -e .
```

## Verification Commands

```bash
python check_system.py          # Quick check (2 seconds)
python dependencies.py          # Detailed dependency check
python verify_installation.py   # Full system test with functionality checks
python dependencies.py --save-freeze  # Save exact versions
```

## Running Comparisons

### GUI Mode (Interactive)
```bash
python main.py              # Launches interactive dialog
python main.py --gui        # Explicitly request GUI mode
```

### CLI Mode - Minimal (uses defaults)
```bash
# Only specify base directory, uses 'new' and 'known_good' subdirs by default
python main.py --base-dir /path/to/project
```

### CLI Mode - Basic
```bash
python main.py \
  --base-dir /path/to/project \
  --new-dir new_images \
  --known-good-dir baseline_images
```

### CLI Mode - 3D Rendering (with histogram equalization)
```bash
python main.py \
  --base-dir ./renders \
  --new-dir current \
  --known-good-dir baseline \
  --use-histogram-eq \
  --color-distance-threshold 20.0 \
  --min-contour-area 100 \
  --highlight-color "0,0,255"
```

### CLI Mode - Full Options
```bash
python main.py \
  --base-dir ./images \
  --new-dir new \
  --known-good-dir good \
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

### Common Flags
```bash
--open-report               # Auto-open summary report in browser
--gui                       # Force GUI mode instead of CLI
--skip-dependency-check     # Skip dependency check (faster)
--check-dependencies        # Check dependencies only and exit
```

## Common Configurations

### Strict Comparison (catch everything)
```bash
--pixel-diff-threshold 0.001 \
--pixel-change-threshold 1 \
--ssim-threshold 0.99 \
--diff-enhancement 10.0
```

### Lenient Comparison (major changes only)
```bash
--pixel-diff-threshold 1.0 \
--pixel-change-threshold 5 \
--ssim-threshold 0.90 \
--color-distance-threshold 30.0 \
--min-contour-area 200
```

### 3D Rendering Comparison
```bash
--use-histogram-eq \
--color-distance-threshold 20.0 \
--min-contour-area 100 \
--ssim-threshold 0.93
```

## Highlight Colors

```bash
--highlight-color "255,0,0"    # Red
--highlight-color "0,255,0"    # Green  
--highlight-color "0,0,255"    # Blue
--highlight-color "255,255,0"  # Yellow
--highlight-color "255,0,255"  # Magenta
--highlight-color "0,255,255"  # Cyan
--highlight-color "255,128,0"  # Orange
```

## Git Commands

```bash
# Initial setup
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main

# Regular workflow
git status
git add .
git commit -m "Description"
git push

# Branching
git checkout -b feature-name
git checkout main
git merge feature-name

# Updating from remote
git pull
```

## Package Installation (if installed via setup.py)

```bash
# After pip install -e .
imgcompare --help               # Run main program
imgcompare-check               # Run system check
imgcompare-deps                # Check dependencies
imgcompare-verify              # Run verification tests
```

## Directory Structure

```
project/
├── baseline_images/     # Known good reference images
│   ├── image1.png
│   └── image2.png
├── new_images/         # New images to test
│   ├── image1.png
│   └── image2.png
├── diffs/             # Generated diff images (auto-created)
└── reports/           # HTML reports (auto-created)
    ├── summary.html
    ├── image1.png.html
    └── results.json
```

## Troubleshooting

```bash
# Missing dependencies
python dependencies.py          # See what's missing

# tkinter issues (Linux)
sudo apt-get install python3-tk

# OpenCV issues
pip uninstall opencv-python
pip install opencv-python-headless

# Verify everything works
python verify_installation.py

# Check Python version
python --version                # Need 3.8+
```

## Output Files

- `summary.html` - Overview sorted by difference
- `[filename].html` - Detailed report per image
- `results.json` - Machine-readable data
- `diff_[filename]` - Enhanced difference image
- `annotated_[filename]` - Image with bounding boxes

## Environment Variables (if needed)

```bash
# Force specific matplotlib backend
export MPLBACKEND=Agg

# Disable OpenCV GUI warnings
export OPENCV_LOG_LEVEL=ERROR
```

## Quick Tips

1. **Start with GUI** for first-time configuration
2. **Use histogram equalization** for 3D renders
3. **Increase color threshold** (20-30) for lighting variations
4. **Lower SSIM threshold** (0.90) for lenient matching
5. **Increase min contour area** (100-200) for cleaner boxes on large images
6. **Try different highlight colors** for different test runs
7. **Use `--skip-dependency-check`** after first successful run
8. **Check summary.html first** to see biggest differences
9. **Press ESC** to close full-size overlays
10. **Use CLI mode** for CI/CD automation
