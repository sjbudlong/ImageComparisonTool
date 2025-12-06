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

# Don't import ImageComparator here - it requires skimage
# We'll import it later when we actually need it

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

    # Historical tracking arguments
    parser.add_argument(
        "--build-number",
        type=str,
        default=None,
        help="Build number or identifier for this comparison run (for historical tracking)",
    )
    parser.add_argument(
        "--commit-hash",
        type=str,
        default=None,
        help="Git commit hash for reproducibility (allows recreating exact environment)",
    )
    parser.add_argument(
        "--enable-history",
        action="store_true",
        default=None,
        help="Enable historical metrics tracking (default: enabled)",
    )
    parser.add_argument(
        "--no-history",
        dest="enable_history",
        action="store_false",
        help="Disable historical metrics tracking",
    )
    parser.add_argument(
        "--history-db",
        type=str,
        default=None,
        help="Path to history database (default: <base-dir>/.imgcomp_history/comparison_history.db)",
    )

    # Retention/cleanup arguments
    parser.add_argument(
        "--cleanup-history",
        action="store_true",
        help="Run retention policy to clean up old historical data",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Maximum number of runs to keep (used with --cleanup-history)",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=None,
        help="Maximum age in days for runs to keep (used with --cleanup-history)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting (used with --cleanup-history)",
    )
    parser.add_argument(
        "--history-stats",
        action="store_true",
        help="Display database statistics and exit",
    )

    # Annotation export arguments
    parser.add_argument(
        "--export-annotations",
        action="store_true",
        help="Export annotations for ML training",
    )
    parser.add_argument(
        "--export-run-id",
        type=int,
        default=None,
        help="Run ID to export annotations for (default: most recent run)",
    )
    parser.add_argument(
        "--export-format",
        type=str,
        default="coco",
        choices=["coco", "yolo"],
        help="Annotation export format (default: coco)",
    )
    parser.add_argument(
        "--export-output",
        type=str,
        default=None,
        help="Output path for exported annotations (default: .imgcomp_history/exports/)",
    )

    # FLIP (perceptual metric) arguments
    parser.add_argument(
        "--enable-flip",
        action="store_true",
        help="Enable NVIDIA FLIP perceptual image comparison (opt-in for performance)",
    )
    parser.add_argument(
        "--flip-pixels-per-degree",
        type=float,
        default=67.0,
        help="FLIP viewing distance parameter (67.0 = 0.7m on 24\" 1080p display)",
    )
    parser.add_argument(
        "--flip-colormaps",
        type=str,
        nargs="+",
        default=["viridis"],
        help="FLIP heatmap colormaps to generate (viridis, jet, turbo, magma)",
    )
    parser.add_argument(
        "--flip-default-colormap",
        type=str,
        default="viridis",
        help="Default FLIP colormap for reports (must be in --flip-colormaps)",
    )

    # Visualization toggle arguments
    parser.add_argument(
        "--show-flip",
        dest="show_flip_visualization",
        action="store_true",
        default=True,
        help="Show FLIP visualizations in reports (default: True)",
    )
    parser.add_argument(
        "--no-show-flip",
        dest="show_flip_visualization",
        action="store_false",
        help="Hide FLIP visualizations in reports",
    )
    parser.add_argument(
        "--show-ssim",
        dest="show_ssim_visualization",
        action="store_true",
        default=True,
        help="Show SSIM visualizations in reports (default: True)",
    )
    parser.add_argument(
        "--no-show-ssim",
        dest="show_ssim_visualization",
        action="store_false",
        help="Hide SSIM visualizations in reports",
    )
    parser.add_argument(
        "--show-pixel-diff",
        dest="show_pixel_diff_visualization",
        action="store_true",
        default=True,
        help="Show pixel difference visualizations in reports (default: True)",
    )
    parser.add_argument(
        "--no-show-pixel-diff",
        dest="show_pixel_diff_visualization",
        action="store_false",
        help="Hide pixel difference visualizations in reports",
    )
    parser.add_argument(
        "--show-color-distance",
        dest="show_color_distance_visualization",
        action="store_true",
        default=True,
        help="Show color distance visualizations in reports (default: True)",
    )
    parser.add_argument(
        "--no-show-color-distance",
        dest="show_color_distance_visualization",
        action="store_false",
        help="Hide color distance visualizations in reports",
    )
    parser.add_argument(
        "--show-histogram",
        dest="show_histogram_visualization",
        action="store_true",
        default=True,
        help="Show histogram visualizations in reports (default: True)",
    )
    parser.add_argument(
        "--no-show-histogram",
        dest="show_histogram_visualization",
        action="store_false",
        help="Hide histogram visualizations in reports",
    )
    parser.add_argument(
        "--show-dimension",
        dest="show_dimension_visualization",
        action="store_true",
        default=True,
        help="Show dimension check visualizations in reports (default: True)",
    )
    parser.add_argument(
        "--no-show-dimension",
        dest="show_dimension_visualization",
        action="store_false",
        help="Hide dimension check visualizations in reports",
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

        # Determine history setting (default: True unless explicitly disabled)
        enable_history = True
        if args.enable_history is False:
            enable_history = False
        elif args.enable_history is True:
            enable_history = True

        # Convert history_db path to Path if provided
        history_db_path = Path(args.history_db) if args.history_db else None

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
                # Historical tracking
                enable_history=enable_history,
                build_number=args.build_number,
                commit_hash=args.commit_hash,
                history_db_path=history_db_path,
                # FLIP configuration
                enable_flip=args.enable_flip,
                flip_pixels_per_degree=args.flip_pixels_per_degree,
                flip_colormaps=args.flip_colormaps,
                flip_default_colormap=args.flip_default_colormap,
                # Visualization toggles
                show_flip_visualization=args.show_flip_visualization,
                show_ssim_visualization=args.show_ssim_visualization,
                show_pixel_diff_visualization=args.show_pixel_diff_visualization,
                show_color_distance_visualization=args.show_color_distance_visualization,
                show_histogram_visualization=args.show_histogram_visualization,
                show_dimension_visualization=args.show_dimension_visualization,
            ),
            args,
        )


def handle_history_commands(args, base_dir: Path) -> bool:
    """
    Handle history-related commands (cleanup, statistics).

    Args:
        args: Parsed command line arguments
        base_dir: Base directory for locating history database

    Returns:
        True if a history command was handled (should exit), False otherwise
    """
    # Determine database path
    if args.history_db:
        db_path = Path(args.history_db)
    else:
        db_path = base_dir / ".imgcomp_history" / "comparison_history.db"

    # Check if database exists
    if not db_path.exists():
        logger.error(f"History database not found: {db_path}")
        logger.info("Run a comparison with --enable-history to create the database first")
        return True

    # Import history modules
    try:
        from history import Database, RetentionPolicy
    except ImportError as e:
        logger.error(f"Failed to import history modules: {e}")
        return True

    # Initialize database
    try:
        db = Database(db_path)
        logger.info(f"Connected to history database: {db_path}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return True

    # Handle --history-stats
    if args.history_stats:
        logger.info("=== Database Statistics ===")
        policy = RetentionPolicy(db, keep_all_runs=True)
        stats = policy.get_statistics()

        logger.info(f"Total runs: {stats['total_runs']}")
        logger.info(f"Total results: {stats['total_results']}")
        logger.info(f"Runs with annotations: {stats['annotated_runs']}")
        logger.info(f"Runs with anomalies: {stats['anomalous_runs']}")

        if stats['oldest_run']:
            logger.info(f"Oldest run: {stats['oldest_run']}")
            logger.info(f"Newest run: {stats['newest_run']}")

        return True

    # Handle --cleanup-history
    if args.cleanup_history:
        # Determine retention policy
        keep_all = not (args.max_runs or args.max_age_days)

        if keep_all:
            logger.warning("No retention limits specified (--max-runs or --max-age-days)")
            logger.info("Use --max-runs N or --max-age-days N to set retention limits")
            return True

        logger.info("=== Retention Policy Cleanup ===")
        logger.info(f"Keep all runs: {keep_all}")
        if args.max_runs:
            logger.info(f"Max runs to keep: {args.max_runs}")
        if args.max_age_days:
            logger.info(f"Max age in days: {args.max_age_days}")
        logger.info(f"Dry run: {args.dry_run}")

        # Create retention policy
        policy = RetentionPolicy(
            database=db,
            keep_all_runs=keep_all,
            max_runs_to_keep=args.max_runs,
            max_age_days=args.max_age_days,
            keep_annotated=True,
            keep_anomalies=True,
        )

        # Apply retention
        result = policy.apply_retention(dry_run=args.dry_run)

        logger.info(f"Runs evaluated: {result['runs_evaluated']}")
        logger.info(f"Runs eligible for deletion: {result['runs_eligible']}")
        logger.info(f"Runs protected: {result['runs_protected']}")

        if args.dry_run:
            logger.info(f"Would delete: {result['runs_deleted']} runs")
            if result['run_ids_deleted']:
                logger.info(f"Run IDs: {result['run_ids_deleted']}")
        else:
            logger.info(f"Deleted: {result['runs_deleted']} runs")
            if result['runs_deleted'] > 0:
                logger.info("Database cleanup complete!")

        return True

    # Handle --export-annotations
    if args.export_annotations:
        logger.info("=== Export Annotations ===")

        # Import annotation modules
        try:
            from annotations import ExportManager
        except ImportError as e:
            logger.error(f"Failed to import annotation modules: {e}")
            return True

        # Determine run_id
        run_id = args.export_run_id
        if run_id is None:
            # Get most recent run
            try:
                rows = db.execute_query("SELECT run_id FROM runs ORDER BY timestamp DESC LIMIT 1")
                if rows:
                    run_id = rows[0]["run_id"]
                    logger.info(f"Using most recent run: {run_id}")
                else:
                    logger.error("No runs found in database")
                    return True
            except Exception as e:
                logger.error(f"Failed to query recent run: {e}")
                return True

        # Determine output path
        export_format = args.export_format.lower()
        if args.export_output:
            output_path = Path(args.export_output)
        else:
            # Default: .imgcomp_history/exports/
            exports_dir = base_dir / ".imgcomp_history" / "exports"
            if export_format == "coco":
                output_path = exports_dir / f"annotations_run_{run_id}.json"
            else:  # yolo
                output_path = exports_dir / f"labels_run_{run_id}"

        # Export annotations
        try:
            export_manager = ExportManager(db, base_dir)
            logger.info(f"Exporting annotations for run {run_id} in {export_format.upper()} format")
            logger.info(f"Output: {output_path}")

            result = export_manager.export(run_id, export_format, output_path)

            if result["success"]:
                logger.info(f"Export successful!")
                logger.info(f"  Annotations: {result['annotation_count']}")
                if export_format == "coco":
                    logger.info(f"  Images: {result['image_count']}")
                    logger.info(f"  Categories: {result['category_count']}")
                else:  # yolo
                    logger.info(f"  Label files: {result['file_count']}")
                    logger.info(f"  Classes: {result['class_count']}")
                logger.info(f"  Output: {result['output_path']}")
            else:
                logger.warning("Export completed with no annotations found")
        except Exception as e:
            logger.error(f"Failed to export annotations: {e}")
            import traceback
            traceback.print_exc()
            return True

        return True

    return False


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
        # Check if history commands were requested
        if "--cleanup-history" in sys.argv or "--history-stats" in sys.argv or "--export-annotations" in sys.argv:
            # Need base-dir for history commands
            if "--base-dir" not in sys.argv:
                logger.error("--base-dir is required for history commands")
                sys.exit(1)

            # Re-parse to get args
            parser = argparse.ArgumentParser()
            parser.add_argument("--base-dir", type=str, required=False)
            parser.add_argument("--history-db", type=str, default=None)
            parser.add_argument("--cleanup-history", action="store_true")
            parser.add_argument("--max-runs", type=int, default=None)
            parser.add_argument("--max-age-days", type=int, default=None)
            parser.add_argument("--dry-run", action="store_true")
            parser.add_argument("--history-stats", action="store_true")
            parser.add_argument("--export-annotations", action="store_true")
            parser.add_argument("--export-run-id", type=int, default=None)
            parser.add_argument("--export-format", type=str, default="coco")
            parser.add_argument("--export-output", type=str, default=None)
            temp_args, _ = parser.parse_known_args()

            if temp_args.base_dir:
                if handle_history_commands(temp_args, Path(temp_args.base_dir)):
                    return

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

        # Handle history commands before running comparison
        if args.cleanup_history or args.history_stats:
            if handle_history_commands(args, config.base_dir):
                return

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

    # Import ImageComparator only when needed (requires skimage)
    try:
        from comparator import ImageComparator
    except ImportError as e:
        logger.error("Failed to import ImageComparator. This usually means scikit-image is not installed.")
        logger.error("Please install scikit-image: pip install scikit-image")
        logger.error(f"Error: {e}")
        sys.exit(1)

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
