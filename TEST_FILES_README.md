# Test Launch Files

These test files demonstrate different ways to run the Image Comparison Tool using command-line arguments. Each file exercises a specific use case from the cheatsheet.

## Windows (.bat files)

- **test_basic_cli.bat** - Basic CLI comparison with minimal options
- **test_3d_rendering.bat** - Optimized for 3D rendering comparisons with histogram equalization
- **test_full_options.bat** - Demonstrates all available command-line options
- **test_strict_comparison.bat** - Very sensitive comparison (catches tiny differences)
- **test_lenient_comparison.bat** - Lenient comparison (only flags major changes)
- **test_with_report.bat** - Basic comparison that auto-opens the summary report in browser

### Running on Windows

Simply double-click any `.bat` file, or run from command prompt:

```cmd
test_basic_cli.bat
```

## Linux/Mac (.sh files)

- **test_basic_cli.sh** - Basic CLI comparison with minimal options
- **test_3d_rendering.sh** - Optimized for 3D rendering comparisons with histogram equalization
- **test_full_options.sh** - Demonstrates all available command-line options
- **test_strict_comparison.sh** - Very sensitive comparison (catches tiny differences)
- **test_lenient_comparison.sh** - Lenient comparison (only flags major changes)
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
