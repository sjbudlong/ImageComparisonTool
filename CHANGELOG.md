# Changelog

All notable changes to the Image Comparison Tool are documented here.

## [Latest] - November 24, 2025

### Added

#### Recursive Image Discovery
- Image search now recursively scans subdirectories of `new` and `known_good` folders
- Smart matching strategy: preserves directory structure with filename-based fallback
- Support for nested test organization (e.g., `tests/unit/`, `tests/integration/`)

#### Interactive Metric Descriptions
- Click ? icon next to metric section headers to view explanations
- Descriptions for: Pixel Difference, Structural Similarity, Histogram Analysis
- Styled description boxes with hover effects
- Easy toggle on/off behavior

#### Enhanced Histogram Equalization
- CLAHE (Contrast Limited Adaptive Histogram Equalization) as default method
- LAB color space processing for color images (preserves color info)
- Optional grayscale equalization mode for maximum tonal normalization
- New config options: `use_clahe`, `equalize_to_grayscale`

#### Grayscale Histogram Visualization
- Report pages now show both grayscale (luminance) and RGB channel histograms
- 2×4 grid layout: grayscale in column 0, RGB channels in columns 1-3
- Better comparison of tonal distribution vs. color shifts
- Enhanced histogram visualization with proper scaling

#### Improved Diff Annotation
- Annotated images now use unenhanced diff as target (instead of new image)
- Shows subtle difference visualization with highlighted regions
- Clearer visibility of exact difference areas
- More detail-preserving approach

### Changed

- **config.py**: Updated validation to check recursively for files
- **processor.py**: Rewrote histogram equalization with advanced techniques
- **processor.py**: Enhanced histogram visualization to 2×4 grid layout
- **comparator.py**: Updated image matching logic for nested directories
- **report_generator.py**: Added interactive descriptions, improved CSS/JS
- **readme.md**: Updated feature list and added recent changes reference

### Fixed

- Histogram equalization now preserves color information better
- Report image links work correctly with nested file structures
- Validation checks work recursively across directory trees

### Technical Details

- All changes backward compatible
- 28 tests passing (100%)
- No breaking changes to public APIs
- New config options have sensible defaults

### Documentation

- **RECENT_CHANGES.md**: Comprehensive guide to all changes (detailed explanations)
- **CHANGELOG.md**: This file (quick reference)
- **readme.md**: Updated with recent enhancements section

## Previous Versions

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for historical context on the tool's core architecture and features.

---

## Testing

All tests pass with Python 3.13:
```bash
pytest -v
# 28 passed in ~4 seconds
```

## Compatibility

- Python 3.8+
- Operating Systems: Windows, Linux, macOS
- Tested on: Python 3.13.7

## Known Limitations

- Very large nested directory structures may have slight performance impact
- CLAHE parameters are fixed (can be made configurable if needed)
- Grayscale equalization mode is opt-in (not default, to preserve color)

## Future Roadmap

- CLI options for equalization parameters
- Interactive histogram comparison overlay
- Additional color normalization methods (HSV, YCbCr)
- Performance profiling for large datasets
- Advanced filtering options for noise reduction
