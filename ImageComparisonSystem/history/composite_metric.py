"""
Composite Metric Calculator for image comparison results.

Provides a weighted combination of multiple comparison metrics into a single
composite score for easier trend analysis and anomaly detection.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import ComparisonResult

logger = logging.getLogger(__name__)


# Default normalization parameters (learned from typical image comparison data)
DEFAULT_NORMALIZATION = {
    "pixel_diff_max": 100.0,        # Percent different (0-100%)
    "ssim_min": 0.0,                # SSIM score (0-1, inverted for difference)
    "ssim_max": 1.0,
    "color_distance_max": 441.67,   # Max RGB distance: sqrt(255^2 * 3)
    "histogram_chi_square_max": 2.0, # Typical max for chi-square
}

# Default weights (equal weighting across all metric categories)
DEFAULT_WEIGHTS = {
    "pixel_diff": 0.25,
    "ssim": 0.25,
    "color_distance": 0.25,
    "histogram": 0.25,
}


def normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value to 0-1 scale using min-max normalization.

    Args:
        value: Value to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range

    Returns:
        Normalized value in range [0, 1]

    Example:
        >>> normalize(50, 0, 100)
        0.5
        >>> normalize(75, 0, 100)
        0.75
    """
    if max_val == min_val:
        return 0.0

    normalized = (value - min_val) / (max_val - min_val)

    # Clamp to [0, 1] range
    return max(0.0, min(1.0, normalized))


def safe_get_metric(metrics: Dict[str, Any], category: str, key: str, default: float = 0.0) -> float:
    """
    Safely extract a metric value from the nested metrics dictionary.

    Args:
        metrics: Nested metrics dictionary
        category: Category name (e.g., "Pixel Difference")
        key: Metric key within category
        default: Default value if not found

    Returns:
        Metric value as float, or default if not found

    Example:
        >>> metrics = {"Pixel Difference": {"percent_different": 10.5}}
        >>> safe_get_metric(metrics, "Pixel Difference", "percent_different")
        10.5
    """
    try:
        category_metrics = metrics.get(category, {})
        value = category_metrics.get(key, default)
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


class CompositeMetricCalculator:
    """
    Calculates weighted composite scores from multiple comparison metrics.

    Combines pixel difference, SSIM, color distance, and histogram metrics
    into a single normalized score (0-100 scale) for easier comparison
    and trend analysis.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        normalization: Optional[Dict[str, float]] = None
    ):
        """
        Initialize composite metric calculator.

        Args:
            weights: Custom weights for each metric category. If None, uses equal weights.
                    Keys: pixel_diff, ssim, color_distance, histogram
            normalization: Custom normalization parameters. If None, uses defaults.

        Example:
            >>> calculator = CompositeMetricCalculator()
            >>> # Or with custom weights:
            >>> calculator = CompositeMetricCalculator(
            ...     weights={"pixel_diff": 0.4, "ssim": 0.3, "color_distance": 0.2, "histogram": 0.1}
            ... )
        """
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self.normalization = normalization or DEFAULT_NORMALIZATION.copy()

        # Validate weights
        self._validate_weights()

    def _validate_weights(self) -> None:
        """
        Validate that weights are valid and sum to approximately 1.0.

        Raises:
            ValueError: If weights are invalid
        """
        required_keys = {"pixel_diff", "ssim", "color_distance", "histogram"}
        if not all(key in self.weights for key in required_keys):
            missing = required_keys - set(self.weights.keys())
            raise ValueError(f"Missing weight keys: {missing}")

        # Check all weights are non-negative
        if any(w < 0 for w in self.weights.values()):
            raise ValueError("All weights must be non-negative")

        # Check weights sum to approximately 1.0 (allow small floating point error)
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(
                f"Weights sum to {weight_sum:.3f}, not 1.0. "
                f"Normalizing weights to sum to 1.0"
            )
            # Normalize weights to sum to 1.0
            for key in self.weights:
                self.weights[key] /= weight_sum

    def calculate_composite_score(
        self,
        result: "ComparisonResult"
    ) -> float:
        """
        Calculate composite score for a comparison result.

        Combines all metrics into a single score on 0-100 scale, where:
        - 0 = images are identical (no difference)
        - 100 = images are completely different

        Args:
            result: ComparisonResult with metrics

        Returns:
            Composite score (0-100 scale)

        Example:
            >>> result = ComparisonResult(...)
            >>> score = calculator.calculate_composite_score(result)
            >>> print(f"Composite score: {score:.2f}")
        """
        metrics = result.metrics

        # Extract and normalize pixel difference (already 0-100%)
        pixel_diff = safe_get_metric(metrics, "Pixel Difference", "percent_different", 0.0)
        pixel_diff_norm = normalize(
            pixel_diff,
            0.0,
            self.normalization["pixel_diff_max"]
        )

        # Extract and normalize SSIM (0-1 scale, 1 = identical, so invert for difference)
        ssim_score = safe_get_metric(metrics, "Structural Similarity", "ssim_score", 1.0)
        # Convert SSIM to difference: higher difference = worse match
        ssim_diff = 1.0 - ssim_score
        ssim_diff_norm = normalize(
            ssim_diff,
            self.normalization["ssim_min"],
            self.normalization["ssim_max"]
        )

        # Extract and normalize color distance
        mean_color_distance = safe_get_metric(metrics, "Color Difference", "mean_color_distance", 0.0)
        color_distance_norm = normalize(
            mean_color_distance,
            0.0,
            self.normalization["color_distance_max"]
        )

        # Extract and normalize histogram metrics (average chi-square across RGB channels)
        red_chi = safe_get_metric(metrics, "Histogram Analysis", "red_histogram_chi_square", 0.0)
        green_chi = safe_get_metric(metrics, "Histogram Analysis", "green_histogram_chi_square", 0.0)
        blue_chi = safe_get_metric(metrics, "Histogram Analysis", "blue_histogram_chi_square", 0.0)

        # Average chi-square across channels (some images might not have all channels)
        chi_values = [v for v in [red_chi, green_chi, blue_chi] if v is not None]
        avg_chi_square = sum(chi_values) / len(chi_values) if chi_values else 0.0

        histogram_norm = normalize(
            avg_chi_square,
            0.0,
            self.normalization["histogram_chi_square_max"]
        )

        # Calculate weighted composite score
        composite = (
            self.weights["pixel_diff"] * pixel_diff_norm +
            self.weights["ssim"] * ssim_diff_norm +
            self.weights["color_distance"] * color_distance_norm +
            self.weights["histogram"] * histogram_norm
        )

        # Scale to 0-100 range
        composite_score = composite * 100.0

        logger.debug(
            f"Composite score for {result.filename}: {composite_score:.2f} "
            f"(pixel={pixel_diff_norm:.2f}, ssim={ssim_diff_norm:.2f}, "
            f"color={color_distance_norm:.2f}, hist={histogram_norm:.2f})"
        )

        return composite_score

    def calculate_batch(
        self,
        results: List["ComparisonResult"]
    ) -> List[Tuple["ComparisonResult", float]]:
        """
        Calculate composite scores for multiple results.

        Args:
            results: List of ComparisonResult objects

        Returns:
            List of (ComparisonResult, composite_score) tuples

        Example:
            >>> results_with_scores = calculator.calculate_batch(results)
            >>> for result, score in results_with_scores:
            ...     print(f"{result.filename}: {score:.2f}")
        """
        return [
            (result, self.calculate_composite_score(result))
            for result in results
        ]

    def enrich_results_with_scores(
        self,
        results: List["ComparisonResult"]
    ) -> List["ComparisonResult"]:
        """
        Add composite_score field to ComparisonResult objects in-place.

        Args:
            results: List of ComparisonResult objects

        Returns:
            Same list of results, now with composite_score field populated

        Example:
            >>> results = calculator.enrich_results_with_scores(results)
            >>> print(results[0].composite_score)
            45.2
        """
        for result in results:
            result.composite_score = self.calculate_composite_score(result)

        return results

    def get_weights(self) -> Dict[str, float]:
        """
        Get current weight configuration.

        Returns:
            Dictionary of weights

        Example:
            >>> weights = calculator.get_weights()
            >>> print(weights)
            {'pixel_diff': 0.25, 'ssim': 0.25, ...}
        """
        return self.weights.copy()

    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Update weight configuration.

        Args:
            weights: New weights dictionary

        Raises:
            ValueError: If weights are invalid

        Example:
            >>> calculator.set_weights({
            ...     "pixel_diff": 0.4,
            ...     "ssim": 0.3,
            ...     "color_distance": 0.2,
            ...     "histogram": 0.1
            ... })
        """
        self.weights = weights.copy()
        self._validate_weights()
        logger.info(f"Updated composite metric weights: {self.weights}")

    def get_normalization(self) -> Dict[str, float]:
        """
        Get current normalization parameters.

        Returns:
            Dictionary of normalization parameters

        Example:
            >>> params = calculator.get_normalization()
            >>> print(params['pixel_diff_max'])
            100.0
        """
        return self.normalization.copy()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize calculator configuration to dictionary.

        Returns:
            Dictionary with weights and normalization parameters

        Example:
            >>> config = calculator.to_dict()
            >>> # Can be stored in database or config file
        """
        return {
            "weights": self.weights.copy(),
            "normalization": self.normalization.copy()
        }

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "CompositeMetricCalculator":
        """
        Create calculator from configuration dictionary.

        Args:
            config: Dictionary with weights and normalization parameters

        Returns:
            CompositeMetricCalculator instance

        Example:
            >>> config = {"weights": {...}, "normalization": {...}}
            >>> calculator = CompositeMetricCalculator.from_dict(config)
        """
        return cls(
            weights=config.get("weights"),
            normalization=config.get("normalization")
        )
