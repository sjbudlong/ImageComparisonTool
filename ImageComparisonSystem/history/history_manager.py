"""
History Manager for image comparison results.

Provides high-level interface for persisting and querying historical
comparison data, including run tracking, result storage, and historical
statistics retrieval.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from ..models import ComparisonResult
from .database import Database

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Manages historical image comparison data.

    Provides methods for saving comparison runs, querying historical data,
    and enriching current results with historical statistics.
    """

    def __init__(self, config):
        """
        Initialize HistoryManager.

        Args:
            config: Config object containing history settings
        """
        self.config = config

        # Determine database path
        if config.history_db_path:
            self.db_path = Path(config.history_db_path)
        else:
            # Default: <base_dir>/.imgcomp_history/comparison_history.db
            history_dir = config.base_dir / ".imgcomp_history"
            history_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = history_dir / "comparison_history.db"

        # Initialize database
        self.db = Database(self.db_path)
        logger.info(f"HistoryManager initialized with database: {self.db_path}")

    def save_run(
        self,
        results: List[ComparisonResult],
        config,
        notes: Optional[str] = None
    ) -> int:
        """
        Save a comparison run to the database.

        Persists both run metadata and all comparison results in a transaction.

        Args:
            results: List of ComparisonResult objects
            config: Config object used for this run
            notes: Optional notes about this run

        Returns:
            run_id: Database ID of the saved run

        Example:
            >>> run_id = history_manager.save_run(results, config, notes="Daily regression test")
            >>> print(f"Saved run {run_id}")
        """
        try:
            # Calculate summary statistics
            total_images = len(results)
            if total_images > 0:
                avg_difference = sum(r.percent_different for r in results) / total_images
                max_difference = max(r.percent_different for r in results)
            else:
                avg_difference = 0.0
                max_difference = 0.0

            # Serialize config to JSON (store critical settings)
            config_snapshot = {
                "pixel_diff_threshold": config.pixel_diff_threshold,
                "ssim_threshold": config.ssim_threshold,
                "color_distance_threshold": config.color_distance_threshold,
                "use_histogram_equalization": config.use_histogram_equalization,
                "diff_enhancement_factor": config.diff_enhancement_factor,
            }

            # Insert run record
            run_id = self.db.execute_insert(
                """INSERT INTO runs (
                    build_number, timestamp, base_dir, new_dir, known_good_dir,
                    config_snapshot, total_images, avg_difference, max_difference, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    config.build_number,
                    datetime.now().isoformat(),
                    str(config.base_dir),
                    config.new_dir,
                    config.known_good_dir,
                    json.dumps(config_snapshot),
                    total_images,
                    avg_difference,
                    max_difference,
                    notes,
                ),
            )

            # Save all results
            if results:
                self.save_results(run_id, results, config)

            logger.info(
                f"Saved run {run_id} with {total_images} images "
                f"(avg diff: {avg_difference:.2f}%, max: {max_difference:.2f}%)"
            )
            return run_id

        except Exception as e:
            logger.error(f"Failed to save run: {e}")
            raise

    def save_results(
        self,
        run_id: int,
        results: List[ComparisonResult],
        config=None
    ) -> int:
        """
        Save comparison results for a run.

        Performs batch insert of all results in a single transaction.

        Args:
            run_id: Database ID of the run
            results: List of ComparisonResult objects
            config: Optional Config object for extracting subdirectories. If not provided,
                   uses the manager's stored config.

        Returns:
            Number of results saved

        Example:
            >>> count = history_manager.save_results(run_id, results)
            >>> print(f"Saved {count} results")
        """
        if not results:
            return 0

        # Use provided config or fall back to stored config
        config_to_use = config if config is not None else self.config

        try:
            # Prepare batch insert data
            result_data = []
            for result in results:
                # Extract metrics from the metrics dictionary
                metrics = result.metrics

                # Get subdirectory using the appropriate config
                subdirectory = result.get_subdirectory(config_to_use.new_path)

                # Extract individual metrics with safe defaults
                pixel_metrics = metrics.get("Pixel Difference", {})
                ssim_metrics = metrics.get("Structural Similarity", {})
                color_metrics = metrics.get("Color Difference", {})
                histogram_metrics = metrics.get("Histogram Analysis", {})

                result_data.append((
                    run_id,
                    result.filename,
                    subdirectory,
                    str(result.new_image_path),
                    str(result.known_good_path),

                    # Pixel difference metrics
                    pixel_metrics.get("percent_different"),
                    pixel_metrics.get("changed_pixels"),
                    pixel_metrics.get("mean_absolute_error"),
                    pixel_metrics.get("max_difference"),

                    # SSIM metrics
                    ssim_metrics.get("ssim_score"),
                    ssim_metrics.get("ssim_percentage"),

                    # Color difference metrics
                    color_metrics.get("mean_color_distance"),
                    color_metrics.get("max_color_distance"),
                    color_metrics.get("significant_color_changes"),

                    # Histogram metrics
                    histogram_metrics.get("red_histogram_correlation"),
                    histogram_metrics.get("green_histogram_correlation"),
                    histogram_metrics.get("blue_histogram_correlation"),
                    histogram_metrics.get("red_histogram_chi_square"),
                    histogram_metrics.get("green_histogram_chi_square"),
                    histogram_metrics.get("blue_histogram_chi_square"),

                    # Composite score (if already calculated)
                    getattr(result, "composite_score", None),

                    # Statistical fields (if already calculated)
                    getattr(result, "historical_mean", None),
                    getattr(result, "historical_std_dev", None),
                    getattr(result, "std_dev_from_mean", None),
                    getattr(result, "is_anomaly", None),

                    # Full metrics as JSON backup
                    json.dumps(result.metrics),
                ))

            # Batch insert
            count = self.db.execute_many(
                """INSERT INTO results (
                    run_id, filename, subdirectory, new_image_path, known_good_path,
                    pixel_difference, changed_pixels, mean_absolute_error, max_pixel_difference,
                    ssim_score, ssim_percentage,
                    mean_color_distance, max_color_distance, significant_color_changes,
                    red_histogram_correlation, green_histogram_correlation, blue_histogram_correlation,
                    red_histogram_chi_square, green_histogram_chi_square, blue_histogram_chi_square,
                    composite_score, historical_mean, historical_std_dev, std_dev_from_mean, is_anomaly,
                    metrics_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                result_data,
            )

            logger.debug(f"Saved {count} results for run {run_id}")
            return count

        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise

    def get_run(self, run_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific run by ID.

        Args:
            run_id: Database ID of the run

        Returns:
            Run data as dictionary, or None if not found

        Example:
            >>> run = history_manager.get_run(42)
            >>> print(f"Build: {run['build_number']}, Images: {run['total_images']}")
        """
        try:
            rows = self.db.execute_query(
                "SELECT * FROM runs WHERE run_id = ?",
                (run_id,)
            )

            if rows:
                return dict(rows[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get run {run_id}: {e}")
            return None

    def get_run_by_build_number(self, build_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most recent run with a specific build number.

        Args:
            build_number: Build number to search for

        Returns:
            Run data as dictionary, or None if not found

        Example:
            >>> run = history_manager.get_run_by_build_number("build-1234")
            >>> print(f"Run ID: {run['run_id']}")
        """
        try:
            rows = self.db.execute_query(
                "SELECT * FROM runs WHERE build_number = ? ORDER BY timestamp DESC LIMIT 1",
                (build_number,)
            )

            if rows:
                return dict(rows[0])
            return None

        except Exception as e:
            logger.error(f"Failed to get run by build number {build_number}: {e}")
            return None

    def get_results_for_run(self, run_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all results for a specific run.

        Args:
            run_id: Database ID of the run

        Returns:
            List of result dictionaries

        Example:
            >>> results = history_manager.get_results_for_run(42)
            >>> for result in results:
            ...     print(f"{result['filename']}: {result['composite_score']}")
        """
        try:
            rows = self.db.execute_query(
                "SELECT * FROM results WHERE run_id = ? ORDER BY composite_score DESC",
                (run_id,)
            )

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get results for run {run_id}: {e}")
            return []

    def get_history_for_image(
        self,
        filename: str,
        subdirectory: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical results for a specific image across all runs.

        Args:
            filename: Image filename
            subdirectory: Optional subdirectory filter
            limit: Maximum number of results to return (default: 100)

        Returns:
            List of result dictionaries ordered by timestamp (newest first)

        Example:
            >>> history = history_manager.get_history_for_image("scene1.png", "renders")
            >>> for result in history:
            ...     print(f"{result['timestamp']}: {result['composite_score']}")
        """
        try:
            if subdirectory is not None:
                query = """
                    SELECT r.*, runs.build_number, runs.timestamp
                    FROM results r
                    JOIN runs ON r.run_id = runs.run_id
                    WHERE r.filename = ? AND r.subdirectory = ?
                    ORDER BY runs.timestamp DESC
                    LIMIT ?
                """
                params = (filename, subdirectory, limit)
            else:
                query = """
                    SELECT r.*, runs.build_number, runs.timestamp
                    FROM results r
                    JOIN runs ON r.run_id = runs.run_id
                    WHERE r.filename = ?
                    ORDER BY runs.timestamp DESC
                    LIMIT ?
                """
                params = (filename, limit)

            rows = self.db.execute_query(query, params)
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get history for image {filename}: {e}")
            return []

    def get_all_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve all runs, ordered by timestamp (newest first).

        Args:
            limit: Maximum number of runs to return (default: 50)

        Returns:
            List of run dictionaries

        Example:
            >>> runs = history_manager.get_all_runs(limit=10)
            >>> for run in runs:
            ...     print(f"{run['build_number']}: {run['total_images']} images")
        """
        try:
            rows = self.db.execute_query(
                "SELECT * FROM runs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get all runs: {e}")
            return []

    def get_recent_runs_for_image(
        self,
        filename: str,
        subdirectory: Optional[str] = None,
        count: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Get recent composite scores for an image (for trend analysis).

        Args:
            filename: Image filename
            subdirectory: Optional subdirectory filter
            count: Number of recent runs to retrieve

        Returns:
            List of (timestamp, composite_score) tuples

        Example:
            >>> trends = history_manager.get_recent_runs_for_image("scene1.png", count=5)
            >>> for timestamp, score in trends:
            ...     print(f"{timestamp}: {score}")
        """
        history = self.get_history_for_image(filename, subdirectory, limit=count)

        return [
            (h["timestamp"], h["composite_score"])
            for h in history
            if h["composite_score"] is not None
        ]

    def get_total_run_count(self) -> int:
        """
        Get total number of runs in database.

        Returns:
            Total run count

        Example:
            >>> count = history_manager.get_total_run_count()
            >>> print(f"Total runs: {count}")
        """
        return self.db.get_row_count("runs")

    def get_total_result_count(self) -> int:
        """
        Get total number of results in database.

        Returns:
            Total result count

        Example:
            >>> count = history_manager.get_total_result_count()
            >>> print(f"Total comparisons: {count}")
        """
        return self.db.get_row_count("results")

    def enrich_with_history(
        self,
        results: List[ComparisonResult]
    ) -> List[ComparisonResult]:
        """
        Enrich comparison results with historical statistics.

        Calculates composite scores, retrieves historical data, computes statistics
        (mean, standard deviation), and detects anomalies for each result.

        Args:
            results: List of ComparisonResult objects

        Returns:
            List of enriched ComparisonResult objects with historical statistics

        Example:
            >>> results = history_manager.enrich_with_history(results)
            >>> for result in results:
            ...     if result.is_anomaly:
            ...         print(f"Anomaly: {result.filename} ({result.std_dev_from_mean:.2f}σ)")
        """
        try:
            from .composite_metric import CompositeMetricCalculator
            from .statistics import StatisticsCalculator

            # Initialize calculators
            metric_calculator = CompositeMetricCalculator(
                weights=self.config.composite_metric_weights
            )
            stats_calculator = StatisticsCalculator(
                anomaly_threshold=self.config.anomaly_threshold
            )

            # Step 1: Calculate composite scores for all results
            logger.debug("Calculating composite scores...")
            results = metric_calculator.enrich_results_with_scores(results)

            # Step 2: Gather historical data for each unique image
            logger.debug("Gathering historical data...")
            historical_data = {}

            for result in results:
                # Get subdirectory for this result
                subdirectory = result.get_subdirectory(self.config.new_path)

                # Query historical scores (excluding current run)
                history = self.get_history_for_image(
                    result.filename,
                    subdirectory=subdirectory if subdirectory else None,
                    limit=100  # Last 100 runs
                )

                # Extract composite scores (excluding None values)
                historical_scores = [
                    h["composite_score"]
                    for h in history
                    if h.get("composite_score") is not None
                ]

                historical_data[result.filename] = historical_scores

            # Step 3: Enrich results with statistics
            logger.debug("Calculating statistics and detecting anomalies...")
            results = stats_calculator.enrich_results_batch(results, historical_data)

            # Log summary
            summary = stats_calculator.get_anomaly_summary(results)
            logger.info(
                f"Statistical analysis complete: {summary['results_with_statistics']}/{summary['total_results']} "
                f"with stats, {summary['total_anomalies']} anomalies detected "
                f"({summary['anomaly_rate']:.1%} rate)"
            )

            return results

        except Exception as e:
            logger.error(f"Failed to enrich results with history: {e}")
            # Return results unchanged if enrichment fails
            return results

    def delete_run(self, run_id: int) -> bool:
        """
        Delete a run and all associated results (CASCADE).

        Args:
            run_id: Database ID of the run to delete

        Returns:
            True if deletion successful, False otherwise

        Example:
            >>> success = history_manager.delete_run(42)
            >>> if success:
            ...     print("Run deleted")
        """
        try:
            count = self.db.execute_update(
                "DELETE FROM runs WHERE run_id = ?",
                (run_id,)
            )

            if count > 0:
                logger.info(f"Deleted run {run_id}")
                return True
            else:
                logger.warning(f"Run {run_id} not found")
                return False

        except Exception as e:
            logger.error(f"Failed to delete run {run_id}: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
            logger.debug("HistoryManager closed")
