"""
Statistical Analysis Engine for historical image comparison metrics.

Provides historical statistics calculation, anomaly detection, and trend analysis
for image comparison results over time.
"""

import logging
import statistics
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import ComparisonResult

logger = logging.getLogger(__name__)


class StatisticsCalculator:
    """
    Calculates historical statistics and detects anomalies in comparison metrics.

    Uses historical data to calculate mean, standard deviation, and identify
    statistical anomalies (outliers) based on configurable thresholds.
    """

    def __init__(
        self,
        anomaly_threshold: float = 2.0,
        min_runs_for_stats: int = 3
    ):
        """
        Initialize statistics calculator.

        Args:
            anomaly_threshold: Number of standard deviations for anomaly detection (default: 2.0 = 95% confidence)
            min_runs_for_stats: Minimum number of historical runs required for statistics (default: 3)

        Example:
            >>> calculator = StatisticsCalculator(anomaly_threshold=2.5, min_runs_for_stats=5)
        """
        self.anomaly_threshold = anomaly_threshold
        self.min_runs_for_stats = min_runs_for_stats

    def calculate_historical_stats(
        self,
        historical_scores: List[float]
    ) -> Optional[Tuple[float, float]]:
        """
        Calculate mean and standard deviation from historical scores.

        Args:
            historical_scores: List of historical composite scores for an image

        Returns:
            Tuple of (mean, std_dev), or None if insufficient data

        Example:
            >>> scores = [10.5, 12.3, 11.8, 10.9, 12.1]
            >>> mean, std_dev = calculator.calculate_historical_stats(scores)
            >>> print(f"Mean: {mean:.2f}, StdDev: {std_dev:.2f}")
        """
        if not historical_scores or len(historical_scores) < self.min_runs_for_stats:
            return None

        try:
            mean = statistics.mean(historical_scores)

            # Need at least 2 values for standard deviation
            if len(historical_scores) < 2:
                return (mean, 0.0)

            std_dev = statistics.stdev(historical_scores)

            return (mean, std_dev)

        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            return None

    def detect_anomaly(
        self,
        current_score: float,
        historical_mean: float,
        historical_std_dev: float
    ) -> Tuple[bool, float]:
        """
        Detect if current score is a statistical anomaly.

        An anomaly is detected when the score deviates by more than
        `anomaly_threshold` standard deviations from the historical mean.

        Args:
            current_score: Current composite score
            historical_mean: Historical mean score
            historical_std_dev: Historical standard deviation

        Returns:
            Tuple of (is_anomaly: bool, std_dev_from_mean: float)

        Example:
            >>> is_anomaly, deviation = calculator.detect_anomaly(50.0, 10.0, 5.0)
            >>> if is_anomaly:
            ...     print(f"Anomaly detected! {deviation:.2f} standard deviations from mean")
        """
        # Handle edge case: zero standard deviation (all historical values identical)
        if historical_std_dev == 0.0:
            # If current score differs from mean at all, it's an anomaly
            is_anomaly = abs(current_score - historical_mean) > 0.01
            std_dev_from_mean = float('inf') if is_anomaly else 0.0
            return (is_anomaly, std_dev_from_mean)

        # Calculate how many standard deviations away from mean
        std_dev_from_mean = (current_score - historical_mean) / historical_std_dev

        # Anomaly if absolute deviation exceeds threshold
        is_anomaly = abs(std_dev_from_mean) > self.anomaly_threshold

        return (is_anomaly, std_dev_from_mean)

    def enrich_result_with_statistics(
        self,
        result: "ComparisonResult",
        historical_scores: List[float]
    ) -> "ComparisonResult":
        """
        Enrich a comparison result with historical statistics.

        Adds historical_mean, historical_std_dev, std_dev_from_mean, and is_anomaly
        fields to the result if sufficient historical data exists.

        Args:
            result: ComparisonResult with composite_score already calculated
            historical_scores: List of historical composite scores for this image

        Returns:
            Same ComparisonResult, enriched with statistics

        Example:
            >>> result = calculator.enrich_result_with_statistics(result, [10.5, 12.3, 11.8])
            >>> print(f"Anomaly: {result.is_anomaly}, Deviation: {result.std_dev_from_mean:.2f}σ")
        """
        # Ensure we have a composite score
        if not hasattr(result, 'composite_score') or result.composite_score is None:
            logger.warning(f"Result {result.filename} has no composite_score, skipping statistics")
            return result

        # Calculate historical statistics
        stats = self.calculate_historical_stats(historical_scores)

        if stats is None:
            # Insufficient historical data
            result.historical_mean = None
            result.historical_std_dev = None
            result.std_dev_from_mean = None
            result.is_anomaly = False

            logger.debug(
                f"{result.filename}: Insufficient historical data "
                f"({len(historical_scores)} runs, need {self.min_runs_for_stats})"
            )
            return result

        historical_mean, historical_std_dev = stats

        # Detect anomaly
        is_anomaly, std_dev_from_mean = self.detect_anomaly(
            result.composite_score,
            historical_mean,
            historical_std_dev
        )

        # Enrich result
        result.historical_mean = historical_mean
        result.historical_std_dev = historical_std_dev
        result.std_dev_from_mean = std_dev_from_mean
        result.is_anomaly = is_anomaly

        logger.debug(
            f"{result.filename}: score={result.composite_score:.2f}, "
            f"mean={historical_mean:.2f}, std={historical_std_dev:.2f}, "
            f"deviation={std_dev_from_mean:.2f}σ, anomaly={is_anomaly}"
        )

        return result

    def enrich_results_batch(
        self,
        results: List["ComparisonResult"],
        historical_data: Dict[str, List[float]]
    ) -> List["ComparisonResult"]:
        """
        Enrich multiple results with historical statistics.

        Args:
            results: List of ComparisonResult objects
            historical_data: Dict mapping filename to list of historical scores

        Returns:
            Same list of results, enriched with statistics

        Example:
            >>> historical_data = {
            ...     "image1.png": [10.5, 12.3, 11.8, 10.9],
            ...     "image2.png": [45.2, 43.8, 44.5, 46.1]
            ... }
            >>> results = calculator.enrich_results_batch(results, historical_data)
        """
        for result in results:
            # Get historical scores for this specific image
            historical_scores = historical_data.get(result.filename, [])
            self.enrich_result_with_statistics(result, historical_scores)

        return results

    def get_anomaly_summary(
        self,
        results: List["ComparisonResult"]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics about anomalies in results.

        Args:
            results: List of ComparisonResult objects with statistics

        Returns:
            Dictionary with anomaly summary statistics

        Example:
            >>> summary = calculator.get_anomaly_summary(results)
            >>> print(f"Total anomalies: {summary['total_anomalies']}")
            >>> print(f"Anomaly rate: {summary['anomaly_rate']:.1%}")
        """
        total = len(results)

        # Count results with statistics
        with_stats = sum(
            1 for r in results
            if hasattr(r, 'historical_mean') and r.historical_mean is not None
        )

        # Count anomalies
        anomalies = sum(
            1 for r in results
            if hasattr(r, 'is_anomaly') and r.is_anomaly
        )

        # Find worst deviations
        deviations = [
            (r.filename, r.std_dev_from_mean, r.composite_score)
            for r in results
            if hasattr(r, 'std_dev_from_mean') and r.std_dev_from_mean is not None
        ]
        deviations.sort(key=lambda x: abs(x[1]), reverse=True)

        return {
            "total_results": total,
            "results_with_statistics": with_stats,
            "total_anomalies": anomalies,
            "anomaly_rate": anomalies / with_stats if with_stats > 0 else 0.0,
            "top_deviations": deviations[:10],  # Top 10 worst deviations
            "anomaly_threshold": self.anomaly_threshold,
            "min_runs_required": self.min_runs_for_stats
        }

    def filter_anomalies(
        self,
        results: List["ComparisonResult"],
        include_non_anomalies: bool = False
    ) -> List["ComparisonResult"]:
        """
        Filter results to return only anomalies (or non-anomalies).

        Args:
            results: List of ComparisonResult objects
            include_non_anomalies: If True, returns non-anomalies; if False, returns anomalies

        Returns:
            Filtered list of results

        Example:
            >>> anomalies = calculator.filter_anomalies(results)
            >>> print(f"Found {len(anomalies)} anomalies")
            >>> for result in anomalies:
            ...     print(f"  {result.filename}: {result.std_dev_from_mean:.2f}σ")
        """
        if include_non_anomalies:
            return [
                r for r in results
                if hasattr(r, 'is_anomaly') and not r.is_anomaly
            ]
        else:
            return [
                r for r in results
                if hasattr(r, 'is_anomaly') and r.is_anomaly
            ]

    def get_trend_direction(
        self,
        historical_scores: List[float],
        min_samples: int = 3
    ) -> Optional[str]:
        """
        Determine if scores are trending up, down, or stable.

        Uses simple linear regression to detect trends.

        Args:
            historical_scores: List of historical scores (oldest to newest)
            min_samples: Minimum samples required for trend analysis

        Returns:
            "increasing", "decreasing", "stable", or None if insufficient data

        Example:
            >>> scores = [10.0, 12.0, 15.0, 18.0, 20.0]  # Increasing trend
            >>> trend = calculator.get_trend_direction(scores)
            >>> print(f"Trend: {trend}")
            "increasing"
        """
        if len(historical_scores) < min_samples:
            return None

        # Simple slope calculation (least squares)
        n = len(historical_scores)
        x_values = list(range(n))

        try:
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(historical_scores)

            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, historical_scores))
            denominator = sum((x - x_mean) ** 2 for x in x_values)

            if denominator == 0:
                return "stable"

            slope = numerator / denominator

            # Classify based on slope magnitude
            # Use threshold relative to mean score
            threshold = y_mean * 0.05  # 5% of mean

            if abs(slope) < threshold:
                return "stable"
            elif slope > 0:
                return "increasing"
            else:
                return "decreasing"

        except Exception as e:
            logger.error(f"Failed to calculate trend: {e}")
            return None
