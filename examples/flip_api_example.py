"""
Programmatic API example for NVIDIA FLIP integration.

This script demonstrates how to use FLIP in your own Python code
for programmatic image comparison and analysis.

Prerequisites:
    pip install flip-evaluator>=1.0.0

Usage:
    python examples/flip_api_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ImageComparisonSystem.config import Config
from ImageComparisonSystem.comparator import ImageComparator
from ImageComparisonSystem.history import Database, HistoryManager


def programmatic_comparison():
    """Demonstrate programmatic FLIP comparison API."""
    print("=" * 70)
    print("Programmatic FLIP Comparison API")
    print("=" * 70)
    print()

    # Create configuration
    config = Config(
        base_dir="path/to/your/images",  # Replace with actual path
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        flip_pixels_per_degree=67.0,
        flip_colormaps=["viridis", "jet"],
        flip_default_colormap="viridis",
        enable_history=True,
        build_number="api_test_001",
    )

    # Run comparison
    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"Processed {len(results)} images\n")

    # Analyze FLIP results
    for result in results:
        if "FLIP Perceptual Metric" not in result.metrics:
            continue

        flip = result.metrics["FLIP Perceptual Metric"]

        print(f"Image: {result.filename}")
        print(f"  FLIP Mean:           {flip['flip_mean']:.6f}")
        print(f"  FLIP Max:            {flip['flip_max']:.6f}")
        print(f"  FLIP 95th %ile:      {flip['flip_percentile_95']:.6f}")
        print(f"  FLIP Weighted Median: {flip['flip_weighted_median']:.6f}")
        print(f"  Quality:             {flip['flip_quality_description']}")
        print(f"  Pixels Per Degree:   {flip['pixels_per_degree']}")

        # Check if perceptually significant
        if flip["flip_mean"] > 0.15:
            print(f"  ⚠️  Significant perceptual difference detected!")

        print()


def query_flip_history():
    """Query historical FLIP data from database."""
    print("=" * 70)
    print("Query FLIP Historical Data")
    print("=" * 70)
    print()

    # Open database
    db_path = "path/to/.imgcomp_history/comparison_history.db"  # Replace
    db = Database(db_path)
    history = HistoryManager(db)

    # Get FLIP trend for specific image
    image_name = "test_image.png"  # Replace with actual image name

    print(f"FLIP trend for '{image_name}':\n")

    trend = history.get_metric_trend(
        filename=image_name, metric_category="FLIP Perceptual Metric", metric_key="flip_mean"
    )

    for entry in trend:
        print(f"Build {entry.build_number}:")
        print(f"  FLIP Mean: {entry.metric_value:.6f}")
        print(f"  Timestamp: {entry.timestamp}")
        print()

    db.close()


def calculate_flip_statistics():
    """Calculate statistics across multiple FLIP comparisons."""
    print("=" * 70)
    print("FLIP Statistics Calculation")
    print("=" * 70)
    print()

    config = Config(
        base_dir="path/to/your/images",  # Replace
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    # Extract FLIP means
    flip_means = []
    flip_maxes = []
    for result in results:
        if "FLIP Perceptual Metric" in result.metrics:
            flip = result.metrics["FLIP Perceptual Metric"]
            flip_means.append(flip["flip_mean"])
            flip_maxes.append(flip["flip_max"])

    if not flip_means:
        print("No FLIP metrics found")
        return

    # Calculate statistics
    import statistics

    print(f"FLIP Statistics across {len(flip_means)} images:\n")
    print(f"Mean FLIP Mean:      {statistics.mean(flip_means):.6f}")
    print(f"Median FLIP Mean:    {statistics.median(flip_means):.6f}")
    print(f"StdDev FLIP Mean:    {statistics.stdev(flip_means) if len(flip_means) > 1 else 0:.6f}")
    print(f"Min FLIP Mean:       {min(flip_means):.6f}")
    print(f"Max FLIP Mean:       {max(flip_means):.6f}")
    print()
    print(f"Mean FLIP Max:       {statistics.mean(flip_maxes):.6f}")
    print(f"Max FLIP Max:        {max(flip_maxes):.6f}")
    print()

    # Quality distribution
    quality_counts = {}
    for result in results:
        if "FLIP Perceptual Metric" in result.metrics:
            quality = result.metrics["FLIP Perceptual Metric"]["flip_quality_description"]
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

    print("Quality Distribution:")
    for quality, count in sorted(quality_counts.items()):
        percentage = (count / len(flip_means)) * 100
        print(f"  {quality}: {count} ({percentage:.1f}%)")


def filter_by_flip_threshold():
    """Filter comparison results by FLIP threshold."""
    print("=" * 70)
    print("Filter Results by FLIP Threshold")
    print("=" * 70)
    print()

    config = Config(
        base_dir="path/to/your/images",  # Replace
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        enable_parallel=True,
    )

    comparator = ImageComparator(config)
    results = comparator.compare_all_parallel()

    # Filter by FLIP threshold
    threshold = 0.10  # Moderate perceptual differences
    print(f"Filtering results with FLIP mean > {threshold}\n")

    filtered_results = []
    for result in results:
        if "FLIP Perceptual Metric" in result.metrics:
            flip_mean = result.metrics["FLIP Perceptual Metric"]["flip_mean"]
            if flip_mean > threshold:
                filtered_results.append(result)

    print(f"Found {len(filtered_results)} images exceeding threshold:\n")
    for result in filtered_results:
        flip = result.metrics["FLIP Perceptual Metric"]
        print(f"  {result.filename}")
        print(f"    FLIP Mean: {flip['flip_mean']:.4f} - {flip['flip_quality_description']}")


def custom_flip_weights_example():
    """Example of custom composite metric weights with FLIP."""
    print("=" * 70)
    print("Custom Composite Metric Weights with FLIP")
    print("=" * 70)
    print()

    # Emphasize FLIP for perceptual quality validation
    custom_weights = {
        "flip": 0.50,  # 50% weight to FLIP (perceptual quality is priority)
        "pixel_diff": 0.15,
        "ssim": 0.15,
        "color_distance": 0.10,
        "histogram": 0.10,
    }

    print("Custom weights (emphasizing FLIP):")
    for metric, weight in custom_weights.items():
        print(f"  {metric}: {weight * 100:.0f}%")
    print()

    config = Config(
        base_dir="path/to/your/images",  # Replace
        new_dir="new",
        known_good_dir="known_good",
        enable_flip=True,
        enable_history=True,
        build_number="custom_weights_001",
        composite_metric_weights=custom_weights,
    )

    comparator = ImageComparator(config)
    results = list(comparator.compare_all_streaming())

    print(f"Processed {len(results)} images")
    print("\nComposite scores (50% FLIP weighted):")
    for result in results:
        if hasattr(result, "composite_score") and result.composite_score is not None:
            flip_mean = result.metrics.get("FLIP Perceptual Metric", {}).get("flip_mean", 0)
            print(f"  {result.filename}")
            print(f"    Composite: {result.composite_score:.2f}")
            print(f"    FLIP Mean: {flip_mean:.4f}")


def main():
    """Run all programmatic API examples."""
    print("\n" + "=" * 70)
    print("NVIDIA FLIP Programmatic API Examples")
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

    print("\nNote: Update 'base_dir' paths in the examples before running.\n")
    print("Available functions to call:")
    print("  - programmatic_comparison()")
    print("  - query_flip_history()")
    print("  - calculate_flip_statistics()")
    print("  - filter_by_flip_threshold()")
    print("  - custom_flip_weights_example()")
    print()
    print("Uncomment the function calls below to run specific examples:\n")

    # Uncomment to run examples:
    # programmatic_comparison()
    # query_flip_history()
    # calculate_flip_statistics()
    # filter_by_flip_threshold()
    # custom_flip_weights_example()

    return 0


if __name__ == "__main__":
    sys.exit(main())
