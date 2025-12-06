"""
Debug script to verify FLIP report generation.

This script helps diagnose why FLIP images might not be showing up in HTML reports.

Usage:
    python debug_flip_reports.py --base-dir path/to/test/images
"""

import sys
import argparse
from pathlib import Path

# Add ImageComparisonSystem to path
sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonSystem.config import Config
from ImageComparisonSystem.comparator import ImageComparator


def debug_flip_reports(base_dir: str):
    """Debug FLIP report generation."""
    print("=" * 70)
    print("FLIP Report Generation Debug")
    print("=" * 70)

    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"\n✗ Error: Directory not found: {base_dir}")
        print(f"  Please provide a valid base directory path")
        return 1

    # Create test config
    config = Config(
        base_dir=base_dir,
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        flip_colormaps=["viridis", "jet"],
        flip_default_colormap="viridis",
        show_flip_visualization=True,  # Ensure enabled
    )

    print(f"\nConfiguration:")
    print(f"  Base Directory: {config.base_dir}")
    print(f"  enable_flip: {config.enable_flip}")
    print(f"  show_flip_visualization: {config.show_flip_visualization}")
    print(f"  flip_colormaps: {config.flip_colormaps}")
    print(f"  flip_default_colormap: {config.flip_default_colormap}")

    # Check if directories exist
    print(f"\nDirectory Check:")
    print(f"  New dir exists: {config.new_path.exists()} ({config.new_path})")
    print(f"  Known good dir exists: {config.known_good_path.exists()} ({config.known_good_path})")

    if not config.new_path.exists() or not config.known_good_path.exists():
        print(f"\n✗ Error: Required directories not found")
        print(f"  Make sure '{config.new_dir}' and '{config.known_good_dir}' subdirectories exist")
        return 1

    # Count images
    new_images = list(config.new_path.glob("*.png")) + list(config.new_path.glob("*.jpg"))
    known_images = list(config.known_good_path.glob("*.png")) + list(config.known_good_path.glob("*.jpg"))

    print(f"\nImage Count:")
    print(f"  New images: {len(new_images)}")
    print(f"  Known good images: {len(known_images)}")

    if len(new_images) == 0 or len(known_images) == 0:
        print(f"\n✗ Error: No images found in directories")
        return 1

    # Run comparison
    print(f"\nRunning comparison...")
    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\n✓ Processed {len(results)} image pairs")

    # Check each result
    print(f"\n{'=' * 70}")
    print(f"FLIP Metrics Check")
    print(f"{'=' * 70}")

    flip_count = 0
    error_map_count = 0

    for result in results:
        print(f"\n{result.filename}:")

        # Check FLIP metrics
        has_flip = "FLIP Perceptual Metric" in result.metrics
        print(f"  Has FLIP metrics: {has_flip}")

        if has_flip:
            flip_count += 1
            flip = result.metrics["FLIP Perceptual Metric"]

            # Check error map
            has_error_map = "flip_error_map_array" in flip
            print(f"  Has error map: {has_error_map}")

            if has_error_map:
                error_map_count += 1
                print(f"  ✓ Error map shape: {flip['flip_error_map_array'].shape}")
                print(f"    FLIP mean: {flip.get('flip_mean', 'N/A'):.6f}")
                print(f"    Quality: {flip.get('flip_quality_description', 'N/A')}")
            else:
                print(f"  ✗ ERROR MAP MISSING - FLIP section will not render!")
        else:
            print(f"  ✗ NO FLIP METRICS")
            print(f"    Check if FLIP package is installed:")
            print(f"    pip install flip-evaluator")

    print(f"\n{'=' * 70}")
    print(f"Summary:")
    print(f"  Total results: {len(results)}")
    print(f"  With FLIP metrics: {flip_count}")
    print(f"  With error maps: {error_map_count}")

    if flip_count == 0:
        print(f"\n✗ NO FLIP METRICS FOUND")
        print(f"  Possible causes:")
        print(f"  1. FLIP package not installed")
        print(f"  2. FLIP import failed (check logs)")
        print(f"  3. enable_flip=False in config")
        return 1

    if error_map_count < flip_count:
        print(f"\n⚠️ WARNING: Some results missing error maps ({flip_count - error_map_count} missing)")

    # Check report files
    print(f"\n{'=' * 70}")
    print(f"Report Files Check")
    print(f"{'=' * 70}")

    html_dir = config.html_path
    if html_dir.exists():
        html_files = list(html_dir.glob("*.html"))
        print(f"  Found {len(html_files)} HTML files in {html_dir}")

        # Check first HTML file for FLIP section
        if html_files:
            # Find a detail report (not summary)
            detail_reports = [f for f in html_files if f.stem != "summary"]

            if detail_reports:
                first_html = detail_reports[0]
                print(f"\nInspecting: {first_html.name}")

                try:
                    content = first_html.read_text(encoding="utf-8")

                    has_flip_section = "flip-section" in content.lower()
                    has_flip_tab = "flip-tab-" in content
                    has_flip_metrics_table = "flip-metrics-table" in content
                    has_flip_colormap_tabs = "flip-colormap-tabs" in content
                    has_showFlipTab = "showFlipTab" in content

                    print(f"  Contains 'flip-section': {has_flip_section}")
                    print(f"  Contains 'flip-tab-': {has_flip_tab}")
                    print(f"  Contains 'flip-metrics-table': {has_flip_metrics_table}")
                    print(f"  Contains 'flip-colormap-tabs': {has_flip_colormap_tabs}")
                    print(f"  Contains 'showFlipTab' function: {has_showFlipTab}")

                    if not has_flip_section:
                        print(f"\n  ✗ FLIP SECTION NOT FOUND IN HTML")
                        print(f"     Possible causes:")
                        print(f"     - show_flip_visualization=False")
                        print(f"     - No FLIP metrics in result")
                        print(f"     - Missing flip_error_map_array")
                        print(f"     - Error during FLIP section generation (check logs)")
                    else:
                        print(f"\n  ✓ FLIP SECTION FOUND IN HTML")

                        # Count FLIP heatmap images
                        flip_img_count = content.count('id="flip-tab-')
                        print(f"  ✓ Found {flip_img_count} FLIP colormap tabs")

                except Exception as e:
                    print(f"  ✗ Error reading HTML file: {e}")
    else:
        print(f"  ✗ HTML directory not found: {html_dir}")

    print(f"\n{'=' * 70}")
    print(f"Diagnosis Complete")
    print(f"{'=' * 70}")

    if error_map_count == len(results) and error_map_count > 0:
        print(f"\n✓ SUCCESS: All results have FLIP metrics and error maps")
        print(f"  Reports should display FLIP heatmaps correctly")
        print(f"  Check HTML files in: {config.html_path}")
        return 0
    else:
        print(f"\n⚠️ Issues detected. Review output above for details.")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Debug FLIP report generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_flip_reports.py --base-dir ~/renders/project_alpha
  python debug_flip_reports.py --base-dir C:/renders/test_images

Note: The base directory should contain 'new' and 'known_good' subdirectories
      with matching image files for comparison.
        """,
    )

    parser.add_argument(
        "--base-dir",
        type=str,
        required=True,
        help="Base directory containing 'new' and 'known_good' subdirectories",
    )

    args = parser.parse_args()

    # Check if FLIP is installed
    print("\nPrerequisites Check:")
    try:
        import flip_evaluator

        print(f"✓ FLIP package is installed")
        print(f"  Version: {getattr(flip_evaluator, '__version__', 'unknown')}")
    except ImportError:
        print("✗ FLIP package NOT installed")
        print("  Install with: pip install flip-evaluator>=1.0.0")
        print()
        return 1

    # Check numpy
    try:
        import numpy

        print(f"✓ NumPy installed: {numpy.__version__}")
    except ImportError:
        print("✗ NumPy NOT installed")
        return 1

    # Check PIL
    try:
        from PIL import Image

        print(f"✓ Pillow installed")
    except ImportError:
        print("✗ Pillow NOT installed")
        return 1

    print()

    # Run debug
    return debug_flip_reports(args.base_dir)


if __name__ == "__main__":
    sys.exit(main())
