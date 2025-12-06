"""
Example script demonstrating NVIDIA FLIP perceptual metric usage.

This script shows various ways to use FLIP for image comparison:
- Basic FLIP comparison
- Custom viewing distance (pixels per degree)
- Multiple colormap generation
- FLIP with historical tracking
- Parallel processing with FLIP
- Custom composite metric weights emphasizing FLIP

Prerequisites:
    pip install flip-evaluator>=1.0.0

Run examples:
    python examples/flip_example.py --example basic
    python examples/flip_example.py --example vfx
    python examples/flip_example.py --example parallel
    python examples/flip_example.py --example custom-weights
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ImageComparisonSystem.config import Config
from ImageComparisonSystem.comparator import ImageComparator


def example_basic():
    """Basic FLIP comparison with default settings."""
    print("=" * 70)
    print("EXAMPLE 1: Basic FLIP Comparison")
    print("=" * 70)
    print("Enables FLIP with default settings (67.0 PPD, viridis colormap)")
    print()

    config = Config(
        base_dir="path/to/your/images",  # Replace with actual path
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,  # Enable FLIP analysis
        flip_pixels_per_degree=67.0,  # Default viewing distance
        flip_colormaps=["viridis"],  # Default colormap
        flip_default_colormap="viridis",
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\nProcessed {len(results)} images")
    print("\nFLIP Metrics for each result:")
    for result in results:
        if "FLIP Perceptual Metric" in result.metrics:
            flip = result.metrics["FLIP Perceptual Metric"]
            print(f"\n{result.filename}:")
            print(f"  FLIP Mean:        {flip['flip_mean']:.4f}")
            print(f"  FLIP Max:         {flip['flip_max']:.4f}")
            print(f"  Quality:          {flip['flip_quality_description']}")
            print(f"  95th Percentile:  {flip['flip_percentile_95']:.4f}")


def example_vfx_rendering():
    """VFX rendering QA with FLIP optimized for cinema viewing distance."""
    print("=" * 70)
    print("EXAMPLE 2: VFX Rendering QA with FLIP")
    print("=" * 70)
    print("Cinema viewing distance (42.0 PPD) with multiple colormaps")
    print("Includes historical tracking for trend analysis")
    print()

    config = Config(
        base_dir="path/to/vfx/renders",  # Replace with actual path
        new_dir="latest_render",
        known_good_dir="approved_frames",
        # FLIP settings for cinema viewing
        enable_flip=True,
        flip_pixels_per_degree=42.0,  # 1.0m viewing distance (cinema)
        flip_colormaps=["viridis", "turbo"],  # Multiple colormaps for review
        flip_default_colormap="viridis",
        # Historical tracking
        enable_history=True,
        build_number="v1.2.3",
        # Enable parallel processing for large datasets
        enable_parallel=True,
        max_workers=8,
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    # Find frames with significant perceptual differences
    print(f"\nProcessed {len(results)} frames")
    print("\nFrames with significant perceptual differences (FLIP mean > 0.15):")

    issues_found = False
    for result in results:
        flip_metrics = result.metrics.get("FLIP Perceptual Metric", {})
        flip_mean = flip_metrics.get("flip_mean", 0)
        if flip_mean > 0.15:
            issues_found = True
            print(f"\n⚠️  {result.filename}:")
            print(f"   FLIP Mean: {flip_mean:.4f}")
            print(f"   Quality:   {flip_metrics['flip_quality_description']}")
            print(f"   FLIP Max:  {flip_metrics['flip_max']:.4f}")

    if not issues_found:
        print("\n✓ No significant perceptual differences found")


def example_parallel_processing():
    """Large-scale comparison with parallel processing."""
    print("=" * 70)
    print("EXAMPLE 3: Parallel Processing with FLIP")
    print("=" * 70)
    print("Process large datasets efficiently using multiple CPU cores")
    print()

    config = Config(
        base_dir="path/to/large/dataset",  # Replace with actual path
        new_dir="new",
        known_good_dir="baseline",
        # FLIP enabled
        enable_flip=True,
        flip_colormaps=["viridis"],
        # Parallel processing (recommended for FLIP)
        enable_parallel=True,
        max_workers=8,  # Adjust based on your CPU cores
    )

    print("Starting parallel comparison...")
    comparator = ImageComparator(config)
    results = comparator.compare_all_parallel()  # Use parallel method

    print(f"\n✓ Processed {len(results)} images in parallel")

    # Calculate statistics
    flip_scores = []
    for result in results:
        if "FLIP Perceptual Metric" in result.metrics:
            flip_scores.append(result.metrics["FLIP Perceptual Metric"]["flip_mean"])

    if flip_scores:
        avg_flip = sum(flip_scores) / len(flip_scores)
        max_flip = max(flip_scores)
        print(f"\nFLIP Statistics:")
        print(f"  Average FLIP Mean: {avg_flip:.4f}")
        print(f"  Maximum FLIP Mean: {max_flip:.4f}")
        print(f"  Images analyzed:   {len(flip_scores)}")


def example_custom_weights():
    """Custom composite metric weights emphasizing FLIP."""
    print("=" * 70)
    print("EXAMPLE 4: Custom Composite Metric Weights")
    print("=" * 70)
    print("Emphasize FLIP in composite scoring (40% FLIP, 15% others)")
    print()

    # Custom weights emphasizing FLIP for perceptual quality
    custom_weights = {
        "flip": 0.40,  # 40% weight to FLIP (perceptual quality)
        "pixel_diff": 0.15,  # 15% to pixel difference
        "ssim": 0.15,  # 15% to SSIM
        "color_distance": 0.15,  # 15% to color
        "histogram": 0.15,  # 15% to histogram
    }

    config = Config(
        base_dir="path/to/images",  # Replace with actual path
        new_dir="new",
        known_good_dir="known_good",
        # FLIP settings
        enable_flip=True,
        # Historical tracking with custom weights
        enable_history=True,
        build_number="custom_weights_test",
        composite_metric_weights=custom_weights,
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\nProcessed {len(results)} images")
    print("\nComposite scores (emphasizing FLIP):")
    for result in results:
        if hasattr(result, "composite_score") and result.composite_score is not None:
            print(f"  {result.filename}: {result.composite_score:.2f}")


def example_multiple_colormaps():
    """Generate multiple FLIP heatmap colormaps for comparison."""
    print("=" * 70)
    print("EXAMPLE 5: Multiple FLIP Colormaps")
    print("=" * 70)
    print("Generate all available colormaps for visual comparison")
    print()

    config = Config(
        base_dir="path/to/images",  # Replace with actual path
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        # All available colormaps
        flip_colormaps=["viridis", "jet", "turbo", "magma"],
        flip_default_colormap="viridis",  # Primary for reports
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\nGenerated FLIP heatmaps with {len(config.flip_colormaps)} colormaps")
    print("Check the 'diffs/' directory for:")
    for colormap in config.flip_colormaps:
        print(f"  - flip_heatmap_{colormap}_*.png")


def example_mobile_viewing():
    """FLIP optimized for mobile device viewing distance."""
    print("=" * 70)
    print("EXAMPLE 6: Mobile Device Viewing Distance")
    print("=" * 70)
    print("PPD = 94.0 for close mobile viewing (~0.5m)")
    print()

    config = Config(
        base_dir="path/to/mobile/ui",  # Replace with actual path
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        flip_pixels_per_degree=94.0,  # 0.5m viewing distance (mobile)
        flip_colormaps=["viridis"],
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\nProcessed {len(results)} UI screenshots")
    print("FLIP optimized for mobile viewing distance")


def example_print_inspection():
    """FLIP for print/document inspection at very close distance."""
    print("=" * 70)
    print("EXAMPLE 7: Print Inspection (Very Close Viewing)")
    print("=" * 70)
    print("PPD = 120.0 for very close inspection")
    print()

    config = Config(
        base_dir="path/to/prints",  # Replace with actual path
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        flip_pixels_per_degree=120.0,  # Very close viewing
        flip_colormaps=["jet", "turbo"],  # High-contrast colormaps
        flip_default_colormap="jet",
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"\nProcessed {len(results)} images")
    print("FLIP optimized for close print inspection")


def main():
    """Run examples based on command-line argument."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NVIDIA FLIP Integration Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python examples/flip_example.py --example basic
  python examples/flip_example.py --example vfx
  python examples/flip_example.py --example parallel
  python examples/flip_example.py --example custom-weights
  python examples/flip_example.py --example colormaps
  python examples/flip_example.py --example mobile
  python examples/flip_example.py --example print

Available Examples:
  basic          - Basic FLIP comparison with default settings
  vfx            - VFX rendering QA with cinema viewing distance
  parallel       - Large-scale parallel processing with FLIP
  custom-weights - Custom composite metric weights emphasizing FLIP
  colormaps      - Generate all available colormaps
  mobile         - Mobile device viewing distance
  print          - Print inspection with very close viewing

Note: Update the 'base_dir' paths in each example function before running.
        """,
    )

    parser.add_argument(
        "--example",
        type=str,
        choices=[
            "basic",
            "vfx",
            "parallel",
            "custom-weights",
            "colormaps",
            "mobile",
            "print",
        ],
        required=True,
        help="Which example to run",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("NVIDIA FLIP Example Scripts")
    print("=" * 70)
    print()

    # Check if FLIP is installed
    try:
        import flip_evaluator

        print("✓ FLIP package is installed")
        print(f"  Version: {getattr(flip_evaluator, '__version__', 'unknown')}")
        print()
    except ImportError:
        print("✗ FLIP package is not installed")
        print("  Install with: pip install flip-evaluator>=1.0.0")
        print()
        return 1

    # Run selected example
    examples = {
        "basic": example_basic,
        "vfx": example_vfx_rendering,
        "parallel": example_parallel_processing,
        "custom-weights": example_custom_weights,
        "colormaps": example_multiple_colormaps,
        "mobile": example_mobile_viewing,
        "print": example_print_inspection,
    }

    try:
        examples[args.example]()
        print("\n" + "=" * 70)
        print("Example completed successfully!")
        print("=" * 70)
        print()
        return 0
    except Exception as e:
        print(f"\n✗ Error running example: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
