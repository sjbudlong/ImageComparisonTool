# Test Launch Files

These test files demonstrate different ways to run the Image Comparison Tool using command-line arguments. Each file exercises a specific use case from the cheatsheet.

## Windows (.bat files)

- **test_basic_cli.bat** - Basic CLI comparison with minimal options
- **test_3d_rendering.bat** - Optimized for 3D rendering comparisons with histogram equalization (large figure, high transparency)
- **test_full_options.bat** - Demonstrates all available command-line options including histogram visualization
- **test_histogram_config.bat** - NEW - Examples of different histogram configurations (smooth, detailed, large, grayscale-only)
- **test_strict_comparison.bat** - Very sensitive comparison (catches tiny differences, uses 512 bin histogram)
- **test_lenient_comparison.bat** - Lenient comparison (only flags major changes, uses 64 bin histogram)
- **test_with_report.bat** - Basic comparison that auto-opens the summary report in browser

### Running on Windows

Simply double-click any `.bat` file, or run from command prompt:

```cmd
test_basic_cli.bat
```

Special note for **test_histogram_config.bat**: This runs 4 sequential tests demonstrating different histogram configurations. Each test pauses for review before proceeding to the next one.

## Linux/Mac (.sh files)

- **test_basic_cli.sh** - Basic CLI comparison with minimal options
- **test_3d_rendering.sh** - Optimized for 3D rendering comparisons with histogram equalization (large figure, high transparency)
- **test_full_options.sh** - Demonstrates all available command-line options including histogram visualization
- **test_histogram_config.sh** - NEW - Examples of different histogram configurations (smooth, detailed, large, grayscale-only)
- **test_strict_comparison.sh** - Very sensitive comparison (catches tiny differences, uses 512 bin histogram)
- **test_lenient_comparison.sh** - Lenient comparison (only flags major changes, uses 64 bin histogram)
- **test_with_report.sh** - Basic comparison that auto-opens the summary report in browser

### Running on Linux/Mac

Make scripts executable and run:

```bash
chmod +x test_*.sh
./test_basic_cli.sh
```

Or run directly with bash:

```bash
bash test_basic_cli.sh
```

Special note for **test_histogram_config.sh**: This runs 4 sequential tests demonstrating different histogram configurations. Each test pauses for review before proceeding to the next one.

## Histogram Configuration Options (New Feature)

All test files now support histogram visualization configuration:

- `--histogram-bins N` - Number of histogram bins (64-512, default 256)
  - 64: Smooth overview
  - 256: Balanced (default)
  - 512: Detailed analysis
- `--histogram-width W` - Figure width in inches (default 16)
- `--histogram-height H` - Figure height in inches (default 6)
- `--histogram-gray-alpha A` - Grayscale line transparency (0-1, default 0.7)
- `--histogram-rgb-alpha A` - RGB line transparency (0-1, default 0.7)
- `--histogram-gray-linewidth W` - Grayscale line width (default 2.0)
- `--histogram-rgb-linewidth W` - RGB line width (default 1.5)
- `--show-grayscale` - Show grayscale histogram (default: true)
- `--show-rgb` - Show RGB channel histograms (default: true)

### Histogram Configuration Examples

**Smooth visualization (overview):**
```
--histogram-bins 64 --histogram-width 14 --histogram-height 5
```

**High detail (analysis):**
```
--histogram-bins 512 --histogram-width 18 --histogram-height 7 --histogram-gray-alpha 0.9
```

**Large presentation:**
```
--histogram-bins 256 --histogram-width 20 --histogram-height 8 --histogram-gray-linewidth 2.5
```

**Grayscale only:**
```
--histogram-bins 256 --show-grayscale
```

See **test_histogram_config.bat** or **test_histogram_config.sh** for complete examples.

## Test Data

All tests use the example data in the `examples/` directory:
- **examples/new/** - Contains new/current images to test
- **examples/known_good/** - Contains reference images to compare against
- **examples/reports/** - Generated HTML reports (created on each run)
- **examples/diffs/** - Generated diff images (created on each run)

## Understanding the Tests

### 1. Basic CLI (`test_basic_cli`)
Simplest usage - just specify base directory and subdirectories for new and known_good images.

### 2. 3D Rendering (`test_3d_rendering`)
Optimized for comparing 3D render outputs with:
- Histogram equalization to normalize lighting variations
- Larger contour area threshold (less sensitivity to noise)
- Increased color distance threshold

### 3. Full Options (`test_full_options`)
Shows every available parameter. Customize these values for your use case.

### 4. Strict Comparison (`test_strict_comparison`)
Most sensitive settings - catches even tiny differences:
- 0.001% pixel threshold (vs default 0.01%)
- 0.99 SSIM threshold (vs default 0.95)
- 10x enhancement

### 5. Lenient Comparison (`test_lenient_comparison`)
Least sensitive - only flags major changes:
- 1.0% pixel threshold (vs default 0.01%)
- 0.90 SSIM threshold (vs default 0.95)

### 6. With Report (`test_with_report`)
Same as basic but adds `--open-report` to automatically open the summary in your browser.

## Customizing Tests

Edit any test file to:
- Change `--base-dir` to point to your own image directories
- Adjust threshold values for your specific use case
- Add `--open-report` to auto-open results
- Remove `--skip-dependency-check` to verify dependencies

## Output

All tests output:
- HTML reports in `examples/reports/summary.html`
- Diff images in `examples/diffs/`
- Metrics JSON in `examples/reports/results.json`

Each run automatically cleans old results before generating new ones.
