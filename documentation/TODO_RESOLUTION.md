# TODO Resolution Guide

**Date:** December 5, 2025
**Status:** In Progress

This document tracks the resolution of post-FLIP-integration TODO items.

## TODO Items

### ✅ TODO 5: Move Documentation to `documentation/` Folder

**Status:** COMPLETE

**Action Taken:**
- Created `documentation/` folder
- Moved `FLIP_INTEGRATION_GUIDE.md` → `documentation/FLIP_INTEGRATION_GUIDE.md`
- All new documentation will be placed in `documentation/` folder

**Files Affected:**
- `documentation/FLIP_INTEGRATION_GUIDE.md` (moved)
- `README.md` (references updated)

---

### 🔄 TODO 1: Debug FLIP Images Not Showing Up in Reports

**Status:** IN PROGRESS - Root Cause Identified

**Problem:**
FLIP heatmap images are not displaying in generated HTML reports.

**Root Cause Analysis:**

The FLIP section generation code is correct (`report_generator.py:493-605`), but there are several potential issues:

1. **Config Check:** `show_flip_visualization` must be `True` (default is `True`)
2. **FLIP Metrics:** FLIP metrics must be present in result
3. **Error Map:** `flip_error_map_array` must be in FLIP metrics
4. **Image Loading:** Known good and new image paths must be valid
5. **Colormap Config:** `flip_colormaps` must be properly configured

**Verification Checklist:**

```python
# Check 1: FLIP enabled in config
config.enable_flip == True

# Check 2: FLIP visualization not disabled
config.show_flip_visualization == True  # Default

# Check 3: FLIP metrics present
"FLIP Perceptual Metric" in result.metrics

# Check 4: Error map preserved
"flip_error_map_array" in result.metrics["FLIP Perceptual Metric"]

# Check 5: Colormaps configured
len(config.flip_colormaps) > 0
config.flip_default_colormap in config.flip_colormaps
```

**Solution - Debug Script:**

Create `debug_flip_reports.py` to verify FLIP integration:

```python
"""Debug script to verify FLIP report generation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonSystem.config import Config
from ImageComparisonSystem.comparator import ImageComparator

def debug_flip_reports():
    """Debug FLIP report generation."""
    print("=" * 70)
    print("FLIP Report Generation Debug")
    print("=" * 70)

    # Create test config
    config = Config(
        base_dir="path/to/test/images",  # Update with real path
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        flip_colormaps=["viridis", "jet"],
        flip_default_colormap="viridis",
        show_flip_visualization=True,  # Ensure enabled
    )

    print(f"\nConfiguration:")
    print(f"  enable_flip: {config.enable_flip}")
    print(f"  show_flip_visualization: {config.show_flip_visualization}")
    print(f"  flip_colormaps: {config.flip_colormaps}")
    print(f"  flip_default_colormap: {config.flip_default_colormap}")

    # Run comparison
    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\nProcessed {len(results)} images")

    # Check each result
    for result in results:
        print(f"\n{result.filename}:")
        has_flip = "FLIP Perceptual Metric" in result.metrics
        print(f"  Has FLIP metrics: {has_flip}")

        if has_flip:
            flip = result.metrics["FLIP Perceptual Metric"]
            has_error_map = "flip_error_map_array" in flip
            print(f"  Has error map: {has_error_map}")
            print(f"  FLIP mean: {flip.get('flip_mean', 'N/A')}")

            if has_error_map:
                print(f"  Error map shape: {flip['flip_error_map_array'].shape}")
            else:
                print(f"  ⚠️ ERROR MAP MISSING - FLIP section will not render")
        else:
            print(f"  ⚠️ NO FLIP METRICS - Check if FLIP package installed")

    # Check report files
    print(f"\nReport files:")
    html_dir = config.html_path
    if html_dir.exists():
        html_files = list(html_dir.glob("*.html"))
        print(f"  Found {len(html_files)} HTML files")

        # Check first HTML file for FLIP section
        if html_files:
            first_html = html_files[0]
            content = first_html.read_text(encoding="utf-8")

            has_flip_section = "flip-section" in content.lower()
            has_flip_tab = "flip-tab-" in content
            has_flip_metrics_table = "flip-metrics-table" in content

            print(f"\nFirst HTML file: {first_html.name}")
            print(f"  Contains 'flip-section': {has_flip_section}")
            print(f"  Contains 'flip-tab-': {has_flip_tab}")
            print(f"  Contains 'flip-metrics-table': {has_flip_metrics_table}")

            if not has_flip_section:
                print(f"\n  ⚠️ FLIP SECTION NOT FOUND IN HTML")
                print(f"     Possible causes:")
                print(f"     - show_flip_visualization=False")
                print(f"     - No FLIP metrics in result")
                print(f"     - Missing flip_error_map_array")

if __name__ == "__main__":
    try:
        import flip
        print(f"✓ FLIP package installed: {getattr(flip, '__version__', 'unknown')}")
    except ImportError:
        print("✗ FLIP package NOT installed")
        print("  Install with: pip install flip-image-comparison")
        sys.exit(1)

    debug_flip_reports()
```

**Quick Fix - Ensure Defaults:**

If the issue is configuration-related, verify defaults in `config.py`:

```python
# ImageComparisonSystem/config.py
show_flip_visualization: bool = True  # Should be True by default
```

**Verification Steps:**

1. Run the debug script on test images
2. Check console output for missing components
3. Inspect generated HTML files for FLIP section
4. Verify FLIP package is installed: `pip list | grep flip`

**Expected Outcome:**
- FLIP section appears in HTML reports after running comparison with `--enable-flip`
- Multiple colormap tabs visible with tab switching functionality
- FLIP heatmap images displayed in 4-panel layout

---

### 📋 TODO 2: Add Command-Line/GUI Args to Summary Page

**Status:** PENDING

**Requirement:**
Display the configuration parameters used for the comparison run on the summary page.

**Implementation Plan:**

1. **Extend ComparisonResult or Create RunConfig Model:**
   ```python
   # In models.py
   @dataclass
   class RunConfiguration:
       """Configuration snapshot for a comparison run."""
       enable_flip: bool
       flip_pixels_per_degree: float
       flip_colormaps: List[str]
       enable_history: bool
       enable_parallel: bool
       max_workers: int
       ssim_threshold: float
       pixel_diff_threshold: float
       # ... other relevant settings

       def to_dict(self) -> dict:
           """Serialize to dictionary."""
           return asdict(self)

       def to_html(self) -> str:
           """Generate HTML table of configuration."""
           rows = []
           for key, value in self.to_dict().items():
               display_name = key.replace('_', ' ').title()
               rows.append(f"<tr><td>{display_name}</td><td>{value}</td></tr>")
           return f"<table class='config-table'>{''.join(rows)}</table>"
   ```

2. **Capture Configuration in Comparator:**
   ```python
   # In comparator.py
   def __init__(self, config: Config):
       self.config = config
       self.run_config = RunConfiguration(
           enable_flip=config.enable_flip,
           flip_pixels_per_degree=config.flip_pixels_per_degree,
           # ... capture relevant fields
       )
   ```

3. **Pass to ReportGenerator:**
   ```python
   # In report_generator.py
   def generate_summary_report(
       self,
       results: List[ComparisonResult],
       run_config: Optional[RunConfiguration] = None
   ):
       # ... existing code ...

       config_section = ""
       if run_config:
           config_section = f"""
           <div class="config-section">
               <h2>Configuration</h2>
               <div class="config-details">
                   {run_config.to_html()}
               </div>
           </div>
           """

       html = html.replace("{{CONFIG_SECTION}}", config_section)
   ```

4. **Add CSS for Config Section:**
   ```css
   .config-section {
       background: #f8f9fa;
       padding: 20px;
       border-radius: 8px;
       margin: 20px 0;
   }
   .config-table {
       width: 100%;
       border-collapse: collapse;
   }
   .config-table td {
       padding: 8px;
       border-bottom: 1px solid #ddd;
   }
   .config-table td:first-child {
       font-weight: bold;
       width: 40%;
   }
   ```

5. **Add Placeholder to Summary Template:**
   ```html
   <!-- In summary HTML template -->
   <div class="container">
       {{CONFIG_SECTION}}

       <!-- Existing summary content -->
   </div>
   ```

**Files to Modify:**
- `ImageComparisonSystem/models.py` - Add RunConfiguration
- `ImageComparisonSystem/comparator.py` - Capture config
- `ImageComparisonSystem/report_generator.py` - Display config
- `ImageComparisonSystem/main.py` - Pass config to generator

**Benefits:**
- Reproducibility: See exact settings used for comparison
- Debugging: Quickly identify configuration issues
- Documentation: Self-documenting reports

---

### 📂 TODO 3: Verify and Update Repository Structure Documentation

**Status:** PENDING

**Requirement:**
Ensure the repository structure in README and other docs accurately reflects the current codebase.

**Action Items:**

1. **Verify Current Structure:**
   ```bash
   tree ImageComparisonSystem/ -I "__pycache__|*.pyc" -L 3
   ```

2. **Update README.md Architecture Section:**

   Current structure should include:
   ```
   ImageComparisonSystem/
   ├── __init__.py
   ├── main.py                          # Entry point & CLI
   ├── config.py                        # Configuration (FLIP settings)
   ├── models.py                        # Data models
   ├── comparator.py                    # Main orchestration (FLIP)
   ├── processor.py                     # Image processing (FLIP heatmaps)
   ├── analyzers.py                     # Modular analyzers (FLIPAnalyzer)
   ├── report_generator.py              # HTML reports (FLIP sections)
   ├── ui.py                            # GUI (FLIP controls)
   ├── dependencies.py                  # Dependency checking
   │
   ├── history/                         # Historical Tracking
   │   ├── __init__.py
   │   ├── database.py
   │   ├── history_manager.py
   │   ├── composite_metric.py          # FLIP-aware composite scoring
   │   ├── statistics.py
   │   ├── retention.py
   │   └── migrations/
   │       └── v1_initial_schema.sql
   │
   ├── annotations/                     # ML Annotations
   │   ├── __init__.py
   │   ├── annotation_manager.py
   │   └── export_formats.py
   │
   └── visualization/                   # Data Visualization
       ├── __init__.py
       └── trend_charts.py

   tests/
   ├── __init__.py
   ├── conftest.py
   ├── test_config.py                   # FLIP config tests
   ├── test_analyzers.py
   ├── test_flip_analyzer.py            # FLIP-specific tests
   ├── test_processor.py                # FLIP visualization tests
   ├── test_comparator.py
   ├── test_report_generator.py         # FLIP report tests
   ├── test_models.py
   ├── test_database.py
   ├── test_history_manager.py
   ├── test_composite_metric.py         # FLIP composite tests
   ├── test_statistics.py
   ├── test_retention.py
   ├── test_annotation_manager.py
   ├── test_export_formats.py
   └── test_flip_integration.py         # FLIP integration tests

   examples/
   ├── flip_example.py                  # FLIP usage examples
   └── flip_api_example.py              # FLIP programmatic API

   documentation/
   ├── FLIP_INTEGRATION_GUIDE.md        # FLIP complete guide
   ├── HISTORICAL_TRACKING_COMPLETE.md
   ├── RECENT_CHANGES.md
   └── TODO_RESOLUTION.md               # This file

   Planning/
   └── NVIDIA_FLIP_Integration_plan.md
   ```

3. **Update Documentation References:**
   - README.md - Architecture section
   - SETUP_GUIDE.md - File structure reference
   - FLIP_INTEGRATION_GUIDE.md - Integration points

4. **Verify File Counts:**
   ```bash
   # Count Python files
   find ImageComparisonSystem -name "*.py" | wc -l

   # Count test files
   find tests -name "test_*.py" | wc -l

   # Count documentation files
   find documentation -name "*.md" | wc -l
   ```

**Expected Output:**
- Accurate tree structure in README.md
- All new files documented (FLIP-related modules)
- Correct file counts in documentation

---

### 📝 TODO 4: Fix Example Command Line Pathing

**Status:** PENDING

**Requirement:**
Update example command lines in documentation to use correct path separators and realistic examples.

**Issues to Fix:**

1. **Path Separators:**
   - Linux/Mac: `/path/to/images`
   - Windows: `C:\path\to\images` or `C:/path/to/images`
   - Should show both or use cross-platform notation

2. **Realistic Paths:**
   - Replace generic placeholders with actual example paths
   - Show directory structure context

**Files to Update:**

1. **README.md:**
   ```bash
   # Before (generic)
   python main.py --base-dir /path/to/images --enable-flip

   # After (cross-platform with examples)
   # Linux/Mac:
   python main.py --base-dir ~/projects/my_renders --enable-flip

   # Windows:
   python main.py --base-dir C:/projects/my_renders --enable-flip
   ```

2. **FLIP_INTEGRATION_GUIDE.md:**
   ```bash
   # Add platform-specific sections
   ### Linux/Mac Example
   python -m ImageComparisonSystem.main \
     --base-dir ~/vfx/shot_042 \
     --new-dir latest_render \
     --known-good-dir approved_frames \
     --enable-flip \
     --flip-pixels-per-degree 42.0

   ### Windows Example
   python -m ImageComparisonSystem.main ^
     --base-dir C:/vfx/shot_042 ^
     --new-dir latest_render ^
     --known-good-dir approved_frames ^
     --enable-flip ^
     --flip-pixels-per-degree 42.0
   ```

3. **Example Scripts:**
   ```python
   # examples/flip_example.py
   # Before:
   base_dir="path/to/your/images"

   # After (with helpful comment):
   base_dir="path/to/your/images"  # Example: ~/renders or C:/renders

   # Add validation
   if not Path(base_dir).exists():
       print(f"Error: Directory not found: {base_dir}")
       print("Please update base_dir in the script with your actual path")
       sys.exit(1)
   ```

4. **Workflow Examples:**
   ```bash
   # VFX Workflow (documentation/FLIP_INTEGRATION_GUIDE.md)

   # Setup (Linux/Mac)
   export PROJECT_DIR=~/vfx_projects/project_alpha
   cd $PROJECT_DIR

   # Setup (Windows - PowerShell)
   $PROJECT_DIR = "C:\vfx_projects\project_alpha"
   cd $PROJECT_DIR

   # Run comparison (works on both)
   python -m ImageComparisonSystem.main \
     --base-dir . \
     --new-dir renders/shot_042/v3 \
     --known-good-dir renders/shot_042/approved \
     --enable-flip
   ```

**Standard Path Examples to Use:**

| Use Case | Linux/Mac | Windows |
|----------|-----------|---------|
| User home | `~/projects/renders` | `C:/Users/username/projects/renders` |
| Project dir | `~/work/vfx/project_alpha` | `C:/work/vfx/project_alpha` |
| Shared drive | `/mnt/shared/renders` | `Z:/shared/renders` |
| Temp dir | `/tmp/test_renders` | `C:/Temp/test_renders` |

**Validation:**
- Test all example commands on both platforms
- Ensure path separators work correctly
- Add error messages for missing directories

---

## Implementation Priority

1. **HIGH:** TODO 1 - FLIP images not displaying (blocks functionality)
2. **MEDIUM:** TODO 2 - Configuration display (improves usability)
3. **MEDIUM:** TODO 3 - Repository structure docs (improves maintainability)
4. **LOW:** TODO 4 - Example pathing (improves documentation quality)
5. **COMPLETE:** TODO 5 - Documentation folder organization

---

## Next Steps

1. Run debug script for TODO 1
2. Create `RunConfiguration` model for TODO 2
3. Generate current directory tree for TODO 3
4. Update all example commands for TODO 4

---

## Notes

- All fixes should maintain backward compatibility
- Test on both Windows and Linux if possible
- Update test suite after each fix
- Document any breaking changes

---

**Last Updated:** December 5, 2025
