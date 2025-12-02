#!/usr/bin/env python3
"""
Image Comparison Tool - Main Entry Point
Compares two sets of images and generates HTML reports with diff analysis.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
import webbrowser
from config import Config
from ui import ComparisonUI
from comparator import ImageComparator

# Setup logging as early as possible
from logging_config import setup_logging, LOG_LEVELS

logger = setup_logging(level=logging.INFO)


def parse_arguments() -> Optional[tuple]:
    """Parse command line arguments and return (Config, args) if all required args present."""
    parser = argparse.ArgumentParser(
        description="Compare images and generate HTML diff reports"
    )

    parser.add_argument(
        "--base-dir", type=str, help="Base directory for all operations"
    )
    parser.add_argument(
        "--new-dir",
        type=str,
        help="Directory containing new images (relative to base-dir)",
    )
    parser.add_argument(
        "--known-good-dir",
        type=str,
        help="Directory containing last known good images (relative to base-dir)",
    )
    parser.add_argument(
        "--diff-dir",
        type=str,
        default="diffs",
        help="Directory for diff outputs (relative to base-dir)",
    )
    parser.add_argument(
        "--html-dir",
        type=str,
        default="reports",
        help="Directory for HTML reports (relative to base-dir)",
    )
    parser.add_argument(
        "--pixel-diff-threshold",
        type=float,
        default=0.01,
        help="Pixel difference threshold percentage (0-100)",
    )
    parser.add_argument(
        "--pixel-change-threshold",
        type=int,
        default=1,
        help="Minimum pixel value change to count as different",
    )
    parser.add_argument(
        "--ssim-threshold",
        type=float,
        default=0.95,
        help="SSIM threshold (0-1, higher = more similar required)",
    )
    parser.add_argument(
        "--color-distance-threshold",
        type=float,
        default=10.0,
        help="RGB color distance threshold",
    )
    parser.add_argument(
        "--min-contour-area",
        type=int,
        default=50,
        help="Minimum contour area for bounding boxes",
    )
    parser.add_argument(
        "--use-histogram-eq",
        action="store_true",
        help="Use histogram equalization to normalize images",
    )
    parser.add_argument(
        "--no-histogram-eq", action="store_true", help="Disable histogram equalization"
    )
    parser.add_argument(
        "--highlight-color",
        type=str,
        default="255,0,0",
        help='RGB color for highlighting differences (e.g., "255,0,0" for red)',
    )
    parser.add_argument(
        "--diff-enhancement",
        type=float,
        default=5.0,
        help="Difference enhancement factor (1.0 = none, higher = more contrast)",
    )
    parser.add_argument(
        "--check-dependencies",
        action="store_true",
        help="Check all dependencies and exit",
    )
    parser.add_argument(
        "--skip-dependency-check",
        action="store_true",
        help="Skip dependency check at startup",
    )
    parser.add_argument(
        "--open-report",
        action="store_true",
        help="Automatically open the summary report in browser after completion",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the GUI mode (interactive dialog) instead of CLI",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set logging level (default: info)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (optional, logs to console by default)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel processing for faster comparisons",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers (default: CPU count)",
    )

    args = parser.parse_args()

    # If --gui flag is set, skip CLI mode and return None to trigger GUI
    if args.gui:
        return None

    # Check if at least base_dir is provided (allow partial CLI args with defaults)
    if args.base_dir:
        # Parse highlight color
        try:
            color_parts = [int(x.strip()) for x in args.highlight_color.split(",")]
            if len(color_parts) != 3:
                raise ValueError
            highlight_color = tuple(color_parts)
        except (ValueError, TypeError):
            logger.warning("Invalid highlight color format, using red (255,0,0)")
            highlight_color = (255, 0, 0)

        # Determine histogram equalization setting
        use_hist_eq = True
        if args.no_histogram_eq:
            use_hist_eq = False
        elif args.use_histogram_eq:
            use_hist_eq = True

        return (
            Config(
                base_dir=Path(args.base_dir),
                new_dir=args.new_dir or "new",
                known_good_dir=args.known_good_dir or "known_good",
                diff_dir=args.diff_dir,
                html_dir=args.html_dir,
                pixel_diff_threshold=args.pixel_diff_threshold,
                pixel_change_threshold=args.pixel_change_threshold,
                ssim_threshold=args.ssim_threshold,
                color_distance_threshold=args.color_distance_threshold,
                min_contour_area=args.min_contour_area,
                use_histogram_equalization=use_hist_eq,
                highlight_color=highlight_color,
                diff_enhancement_factor=args.diff_enhancement,
                enable_parallel=args.parallel,
                max_workers=args.max_workers,
            ),
            args,
        )


def main():
    """Main entry point for the Image Comparison Tool."""
    # Parse arguments first to check for dependency check flag
    args = argparse.Namespace()

    # Handle log level configuration early
    if "--log-level" in sys.argv:
        idx = sys.argv.index("--log-level")
        if idx + 1 < len(sys.argv):
            log_level = sys.argv[idx + 1].lower()
            if log_level in LOG_LEVELS:
                # Reconfigure logger with specified level
                setup_logging(level=LOG_LEVELS[log_level])

    # Handle log file configuration
    if "--log-file" in sys.argv:
        idx = sys.argv.index("--log-file")
        if idx + 1 < len(sys.argv):
            log_file = sys.argv[idx + 1]
            # Reconfigure logger with log file
            setup_logging(log_file=Path(log_file))

    if "--check-dependencies" in sys.argv:
        try:
            from dependencies import DependencyChecker

            DependencyChecker.check_and_exit_if_missing(skip_tkinter=False)
            logger.info("All dependencies satisfied!")
            sys.exit(0)
        except ImportError:
            logger.error("Dependency checker not available")
            sys.exit(1)

    # Run full dependency check unless skipped
    if "--skip-dependency-check" not in sys.argv:
        try:
            from dependencies import DependencyChecker

            # Determine if GUI will be used
            will_use_gui = "--gui" in sys.argv or "--base-dir" not in sys.argv
            DependencyChecker.check_and_exit_if_missing(skip_tkinter=not will_use_gui)
        except ImportError:
            pass  # Already warned in import section

    config = parse_arguments()

    if config is None:
        # Launch UI if not all arguments provided
        logger.info("Launching UI (not all command line arguments provided)...")
        ui = ComparisonUI()
        config = ui.run()

        if config is None:
            logger.info("Operation cancelled by user")
            return
        # When using UI, don't open report by default
        open_report_flag = False
    else:
        config, args = config
        open_report_flag = args.open_report

    # Run the comparison
    logger.info("Starting image comparison...")
    logger.info(f"Base directory: {config.base_dir}")
    logger.info(f"New images: {config.new_dir}")
    logger.info(f"Known good images: {config.known_good_dir}")
    logger.info(
        f"Histogram equalization: {'enabled' if config.use_histogram_equalization else 'disabled'}"
    )
    logger.info(
        f"Parallel processing: {'enabled' if config.enable_parallel else 'disabled'}"
    )
    if config.enable_parallel:
        logger.info(f"Max workers: {config.max_workers or 'CPU count'}")
    logger.info(f"Output will be saved to: {config.html_dir}")

    comparator = ImageComparator(config)

    # Use parallel or sequential processing based on config
    if config.enable_parallel:
        results = comparator.compare_all_parallel()
    else:
        results = comparator.compare_all()

    logger.info("Comparison complete!")
    logger.info(f"{len(results)} image pairs compared")
    report_dir = config.base_dir / config.html_dir
    logger.info(f"Reports saved to: {report_dir}")
    logger.info("Open 'summary.html' to view results")

    # Open report in browser if --open-report flag was provided
    if open_report_flag and results:
        summary_path = report_dir / "summary.html"
        if summary_path.exists():
            try:
                # Convert to absolute path and open in browser
                report_url = summary_path.resolve().as_uri()
                webbrowser.open(report_url)
                logger.info("Opening report in browser...")
            except Exception as e:
                logger.warning(f"Could not open report in browser: {e}")


if __name__ == "__main__":
    main()
