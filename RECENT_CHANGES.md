# Recent Changes & Updates

This document captures all recent enhancements made to the Image Comparison Tool as of November 24, 2025.

## 1. Recursive Image Discovery

### Overview
The image comparison tool now searches **recursively** into subdirectories of the `new` and `known_good` folders, enabling comparison of images organized in nested directory structures.

### Changes Made
- **File**: `ImageComparisonSystem/comparator.py`
  - Updated `_find_images()` method to use `Path.rglob()` for recursive file discovery
  - Filters to only actual files (excludes directories)
  - Supports multiple image formats: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.gif` (case-insensitive)

### Smart Image Matching
When a new image is found, the tool attempts to match it with a known-good reference image using a two-tier strategy:

1. **Relative Path Matching** (preserves directory structure)
   - First looks for a known-good image at the same relative subpath
   - Example: `new/subfolder/test.png` → `known_good/subfolder/test.png`

2. **Fallback Filename Matching** (anywhere in the tree)
   - If no mirrored file exists, searches by filename across the entire `known_good` directory
   - Prefers matches in same-named parent directory when multiple matches exist
   - Example: `new/tests/image.png` searches for `image.png` anywhere under `known_good`

### Configuration Update
- **File**: `ImageComparisonSystem/config.py`
  - Updated `validate()` method to check recursively for files using `Path.rglob()`
  - Ensures at least one file exists anywhere under each directory

## 2. Interactive Metric Descriptions

### Overview
Result pages now display interactive descriptions of the metrics being used. Users can click a question mark icon next to metric headers to reveal detailed explanations.

### Changes Made
- **File**: `ImageComparisonSystem/report_generator.py`
  - Added `METRIC_DESCRIPTIONS` class constant with descriptions for:
    - **Pixel Difference**: Pixel-by-pixel comparison showing % different and RGB distance
    - **Structural Similarity**: SSIM metric (0-1 scale) accounting for luminance, contrast, and structure
    - **Histogram Analysis**: Color distribution analysis per RGB channel
  
  - Updated `_format_metrics()` to generate metric headers with toggleable descriptions
  - Each description is hidden by default and revealed on click
  
  - Enhanced HTML template with:
    - Blue circular question mark icons (`?`)
    - Light gray description boxes with blue left border
    - `toggleDescription()` JavaScript function for show/hide behavior
    - Hover effects on question mark icons

### Visual Design
- Question mark icon appears to the right of each metric section header
- Icon scales up slightly on hover for better interaction feedback
- Description text is displayed in a highlighted box below the header
- Descriptions can be toggled on/off by clicking either the header or the icon

## 3. Unenhanced Diff Image as Annotation Target

### Overview
The annotated image now displays the **unenhanced difference visualization** with bounding boxes, instead of the new image. This provides clearer visibility of exact difference areas without contrast amplification.

### Changes Made
- **File**: `ImageComparisonSystem/comparator.py`
  - Updated `_compare_single_pair()` to create two diff images:
    1. **Unenhanced diff** (enhancement factor = 1.0) → used as annotation target
    2. **Enhanced diff** (configurable enhancement factor) → saved for visualization

  - Bounding boxes now drawn on the unenhanced diff image
  - Difference areas identified using the same unenhanced diff image

### Result
- Annotated image shows subtle difference visualization with highlighted regions
- More detail-preserving than annotating the new image directly
- Enhanced diff still available separately for comparison

## 4. Enhanced Histogram Equalization

### Overview
The histogram equalization now uses advanced techniques to better normalize tonal variations while preserving image quality and color information.

### Improvements
1. **CLAHE (Contrast Limited Adaptive Histogram Equalization)** — new default
   - Less aggressive than standard histogram equalization
   - Preserves local contrast and produces more natural results
   - Uses adaptive 8×8 tiling with clip limit of 2.0
   - Reduces over-enhancement artifacts

2. **LAB Color Space Processing** — for color images
   - Converts RGB → LAB color space for processing
   - Equalizes only the **L (lightness) channel**
   - Preserves color information (A and B channels unchanged)
   - More perceptually accurate than independent RGB channel equalization
   - Avoids color distortion from channel-by-channel processing

3. **Grayscale Equalization Option**
   - Can optionally convert images to grayscale before equalization
   - Enables maximum tonal normalization when needed
   - Controlled via `equalize_to_grayscale` config option

### Changes Made
- **File**: `ImageComparisonSystem/processor.py`
  - Rewrote `equalize_histogram()` method with new parameters:
    - `use_clahe`: Use CLAHE instead of standard equalization (default: `True`)
    - `to_grayscale`: Convert to grayscale for equalization (default: `False`)
  
  - Updated `load_images()` to accept and pass through equalization options

- **File**: `ImageComparisonSystem/config.py`
  - Added new configuration options:
    - `use_clahe` (default: `True`)
    - `equalize_to_grayscale` (default: `False`)

- **File**: `ImageComparisonSystem/comparator.py`
  - Updated `_compare_single_pair()` to pass equalization options from config

## 5. Enhanced Histogram Visualization

### Overview
Result pages now display **both grayscale (luminance) and RGB channel histograms** in a comprehensive 2×4 grid layout, providing complete tonal and color distribution information.

### Changes Made
- **File**: `ImageComparisonSystem/processor.py`
  - Updated `generate_histogram_image()` method to generate 2×4 subplot layout:
    - **Column 0**: Grayscale histograms (luminance)
    - **Columns 1-3**: Individual RGB channel histograms
  
  - Grayscale histograms shown first (larger, more prominent)
  - All images converted to grayscale for luminance calculation
  - RGB channels shown in color (red, green, blue)
  - Clearer titles and legends for each histogram
  - Enhanced grid formatting and layout

### Benefits
- Comprehensive view of both tonal distribution (grayscale) and color composition (RGB)
- Easier to identify tonal shifts versus color shifts
- Better for comparing histogram equalization effectiveness
- More informative than color-only or grayscale-only histograms

## 6. Markdown Report Exporter for CI/CD Integration

### Overview
A new markdown exporter generates machine-readable summary reports optimized for CI/CD pipeline integration (Azure DevOps, GitHub Actions, etc.). Both HTML and Markdown summaries are now generated automatically.

### Features
- **Pipeline-Agnostic Format**: Pure markdown suitable for any CI/CD system
- **Comprehensive Statistics**: Summary of all comparison results with categorization
- **Difference Metrics**: Min, max, and average difference percentages
- **Status Table**: Quick reference for all comparisons with color-coded status
- **Easy Integration**: Markdown can be parsed by scripts or displayed in pipeline summaries

### Changes Made
- **File**: `ImageComparisonSystem/markdown_exporter.py` (new file)
  - New `MarkdownExporter` class for generating markdown reports
  - Methods:
    - `generate_summary()`: Create markdown summary with statistics
    - `generate_comparison_table()`: Build markdown table of results
    - `_get_timestamp()`: Add ISO-format timestamp for audit trails
  
- **File**: `ImageComparisonSystem/report_generator.py`
  - Kept HTML generation separate and intact
  - Delegates markdown generation to `MarkdownExporter`
  - Cleaner separation of concerns

- **File**: `ImageComparisonSystem/comparator.py`
  - Updated `_generate_reports()` to invoke both HTML and markdown export

### Output Files
Both are generated in the reports directory:
- `summary.html` - Interactive HTML dashboard (existing)
- `summary.md` - Markdown summary for CI/CD (new)

### Azure DevOps Integration Example
```yaml
# In azure-pipelines.yml
- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)/reports'
    artifactName: 'image-comparison-reports'

- script: |
    cat reports/summary.md >> $(Build.BuildLogFilePath)
```

### GitHub Actions Integration Example
```yaml
# In workflow file
- name: Generate comparison summary
  run: python -m ImageComparisonSystem.main --base-dir .

- name: Post summary to PR
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const summary = fs.readFileSync('reports/summary.md', 'utf8');
      core.summary.addRaw(summary).write();
```

### Markdown Format Features
- **Statistics Section**: Categorized counts (identical, minor, moderate, major)
- **Metrics Table**: Min/max/average differences with proper formatting
- **Results Table**: Each comparison with filename, percentage, status, and link
- **Navigation Links**: References to HTML reports for detailed viewing
- **Timestamp**: ISO format for audit and traceability

### Benefits for CI/CD
1. **Machine Readable**: Easy to parse with regex or markdown parsers
2. **Pipeline Compatible**: Works with any CI system (Azure DevOps, GitHub, GitLab, Jenkins, etc.)
3. **Trackable**: Timestamps for build correlation
4. **Reportable**: Can be included in build summaries, emails, or notifications
5. **Flexible**: Markdown format is human-readable and can be reformatted as needed

## Summary of Files Modified

| File | Changes |
|------|---------|
| `ImageComparisonSystem/comparator.py` | Recursive search, smart matching, unenhanced diff target, equalization config passing, markdown export integration |
| `ImageComparisonSystem/config.py` | Recursive validation, CLAHE and grayscale equalization options |
| `ImageComparisonSystem/processor.py` | Enhanced equalization, improved histogram visualization |
| `ImageComparisonSystem/report_generator.py` | Interactive metric descriptions, improved CSS/JS |
| `ImageComparisonSystem/markdown_exporter.py` | New markdown export functionality |

## Configuration Examples

### Default Configuration (Recommended)
```python
use_histogram_equalization = True      # Enable tonal normalization
use_clahe = True                       # Use CLAHE (less aggressive)
equalize_to_grayscale = False          # Keep color information
```

### Maximum Tonal Normalization
```python
use_histogram_equalization = True
use_clahe = True
equalize_to_grayscale = True           # Convert to grayscale first
```

### Standard Histogram Equalization (Legacy)
```python
use_histogram_equalization = True
use_clahe = False                      # Use standard cv2.equalizeHist()
equalize_to_grayscale = False
```

## Testing

All changes have been validated with the full test suite:
- ✅ 28 tests passing
- ✅ Config creation and validation
- ✅ Dependency checks
- ✅ Model serialization
- ✅ Image processor functions
- ✅ Integration tests

Run tests with:
```bash
python -m pytest -v
```

## Backward Compatibility

All changes maintain backward compatibility:
- Existing configurations continue to work (new options have sensible defaults)
- Old report format still supported
- Image discovery is additive (flat directories still work alongside nested ones)
- API signatures backward-compatible (new parameters have defaults)

## Future Considerations

- Add configuration UI/CLI options for equalization parameters
- Consider interactive histogram with comparison overlay
- Add more advanced color normalization options
- Performance optimization for very large nested directory structures
