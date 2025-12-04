"""
Unit tests for composite metric calculator.

Tests normalization, score calculation, weight management, and configuration.
"""

import pytest
from pathlib import Path

from ImageComparisonSystem.history.composite_metric import (
    CompositeMetricCalculator,
    normalize,
    safe_get_metric,
    DEFAULT_WEIGHTS,
    DEFAULT_NORMALIZATION
)
from ImageComparisonSystem.models import ComparisonResult


def create_test_result(
    filename: str,
    pixel_diff: float,
    ssim_score: float,
    color_distance: float,
    histogram_chi_square: float
) -> ComparisonResult:
    """Helper to create a test ComparisonResult."""
    return ComparisonResult(
        filename=filename,
        new_image_path=Path("/test/new") / filename,
        known_good_path=Path("/test/known") / filename,
        diff_image_path=Path("/test/diff") / filename,
        annotated_image_path=Path("/test/annotated") / filename,
        metrics={
            "Pixel Difference": {
                "percent_different": pixel_diff,
                "changed_pixels": 1000,
                "mean_absolute_error": 5.5,
                "max_difference": 255,
            },
            "Structural Similarity": {
                "ssim_score": ssim_score,
                "ssim_percentage": (1 - ssim_score) * 100,
            },
            "Color Difference": {
                "mean_color_distance": color_distance,
                "max_color_distance": 150.0,
                "significant_color_changes": 500,
            },
            "Histogram Analysis": {
                "red_histogram_chi_square": histogram_chi_square,
                "green_histogram_chi_square": histogram_chi_square,
                "blue_histogram_chi_square": histogram_chi_square,
            },
        },
        percent_different=pixel_diff,
        histogram_data="base64_data",
    )


class TestNormalize:
    """Test normalize() function."""

    def test_normalize_mid_range(self):
        """Test normalization of mid-range value."""
        assert normalize(50, 0, 100) == 0.5

    def test_normalize_minimum(self):
        """Test normalization of minimum value."""
        assert normalize(0, 0, 100) == 0.0

    def test_normalize_maximum(self):
        """Test normalization of maximum value."""
        assert normalize(100, 0, 100) == 1.0

    def test_normalize_quarter(self):
        """Test normalization of quarter value."""
        assert normalize(25, 0, 100) == 0.25

    def test_normalize_three_quarters(self):
        """Test normalization of three-quarters value."""
        assert normalize(75, 0, 100) == 0.75

    def test_normalize_out_of_range_clamped(self):
        """Test that values outside range are clamped."""
        assert normalize(150, 0, 100) == 1.0  # Clamped to max
        assert normalize(-50, 0, 100) == 0.0  # Clamped to min

    def test_normalize_equal_min_max(self):
        """Test normalization when min equals max."""
        assert normalize(50, 100, 100) == 0.0


class TestSafeGetMetric:
    """Test safe_get_metric() function."""

    def test_get_existing_metric(self):
        """Test retrieving an existing metric."""
        metrics = {"Pixel Difference": {"percent_different": 10.5}}
        value = safe_get_metric(metrics, "Pixel Difference", "percent_different")
        assert value == 10.5

    def test_get_missing_category(self):
        """Test retrieving from missing category returns default."""
        metrics = {"Pixel Difference": {"percent_different": 10.5}}
        value = safe_get_metric(metrics, "Missing Category", "key", default=0.0)
        assert value == 0.0

    def test_get_missing_key(self):
        """Test retrieving missing key returns default."""
        metrics = {"Pixel Difference": {"percent_different": 10.5}}
        value = safe_get_metric(metrics, "Pixel Difference", "missing_key", default=99.9)
        assert value == 99.9

    def test_get_none_value(self):
        """Test retrieving None value returns default."""
        metrics = {"Pixel Difference": {"percent_different": None}}
        value = safe_get_metric(metrics, "Pixel Difference", "percent_different", default=5.0)
        assert value == 5.0


class TestCompositeMetricCalculatorInitialization:
    """Test CompositeMetricCalculator initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default weights."""
        calculator = CompositeMetricCalculator()

        assert calculator.weights == DEFAULT_WEIGHTS
        assert calculator.normalization == DEFAULT_NORMALIZATION

    def test_init_with_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {
            "pixel_diff": 0.4,
            "ssim": 0.3,
            "color_distance": 0.2,
            "histogram": 0.1
        }

        calculator = CompositeMetricCalculator(weights=custom_weights)

        assert calculator.weights == custom_weights

    def test_init_validates_weights_sum(self):
        """Test that weights are normalized if they don't sum to 1.0."""
        bad_weights = {
            "pixel_diff": 0.5,
            "ssim": 0.5,
            "color_distance": 0.5,
            "histogram": 0.5
        }

        calculator = CompositeMetricCalculator(weights=bad_weights)

        # Should be normalized to sum to 1.0
        assert abs(sum(calculator.weights.values()) - 1.0) < 0.001

    def test_init_raises_on_missing_keys(self):
        """Test that missing weight keys raise ValueError."""
        bad_weights = {
            "pixel_diff": 0.5,
            "ssim": 0.5
            # Missing color_distance and histogram
        }

        with pytest.raises(ValueError, match="Missing weight keys"):
            CompositeMetricCalculator(weights=bad_weights)

    def test_init_raises_on_negative_weights(self):
        """Test that negative weights raise ValueError."""
        bad_weights = {
            "pixel_diff": 0.5,
            "ssim": 0.5,
            "color_distance": -0.1,
            "histogram": 0.1
        }

        with pytest.raises(ValueError, match="non-negative"):
            CompositeMetricCalculator(weights=bad_weights)


class TestCompositeScoreCalculation:
    """Test composite score calculation."""

    def test_calculate_identical_images(self):
        """Test score for identical images (should be close to 0)."""
        calculator = CompositeMetricCalculator()

        result = create_test_result(
            filename="identical.png",
            pixel_diff=0.0,
            ssim_score=1.0,
            color_distance=0.0,
            histogram_chi_square=0.0
        )

        score = calculator.calculate_composite_score(result)

        # Should be very close to 0 (identical)
        assert score < 1.0

    def test_calculate_completely_different_images(self):
        """Test score for completely different images (should be close to 100)."""
        calculator = CompositeMetricCalculator()

        result = create_test_result(
            filename="different.png",
            pixel_diff=100.0,
            ssim_score=0.0,
            color_distance=441.67,
            histogram_chi_square=2.0
        )

        score = calculator.calculate_composite_score(result)

        # Should be close to 100 (completely different)
        assert score > 99.0

    def test_calculate_moderate_difference(self):
        """Test score for moderately different images."""
        calculator = CompositeMetricCalculator()

        result = create_test_result(
            filename="moderate.png",
            pixel_diff=50.0,
            ssim_score=0.5,
            color_distance=100.0,
            histogram_chi_square=1.0
        )

        score = calculator.calculate_composite_score(result)

        # Should be in moderate range (30-70)
        assert 30.0 < score < 70.0

    def test_calculate_with_custom_weights(self):
        """Test that custom weights affect the score."""
        # Heavily weight pixel difference
        pixel_heavy_weights = {
            "pixel_diff": 0.7,
            "ssim": 0.1,
            "color_distance": 0.1,
            "histogram": 0.1
        }

        calculator = CompositeMetricCalculator(weights=pixel_heavy_weights)

        result = create_test_result(
            filename="test.png",
            pixel_diff=100.0,  # High pixel diff
            ssim_score=1.0,    # Good SSIM
            color_distance=0.0,
            histogram_chi_square=0.0
        )

        score = calculator.calculate_composite_score(result)

        # Score should be high because pixel diff is weighted heavily
        assert score > 60.0


class TestBatchCalculation:
    """Test batch calculation methods."""

    def test_calculate_batch(self):
        """Test calculating scores for multiple results."""
        calculator = CompositeMetricCalculator()

        results = [
            create_test_result("img1.png", 10.0, 0.95, 10.0, 0.2),
            create_test_result("img2.png", 50.0, 0.5, 100.0, 1.0),
            create_test_result("img3.png", 90.0, 0.1, 300.0, 1.8),
        ]

        results_with_scores = calculator.calculate_batch(results)

        assert len(results_with_scores) == 3
        # Check that scores are in ascending order (more different = higher score)
        assert results_with_scores[0][1] < results_with_scores[1][1] < results_with_scores[2][1]

    def test_enrich_results_with_scores(self):
        """Test enriching results with composite scores in-place."""
        calculator = CompositeMetricCalculator()

        results = [
            create_test_result("img1.png", 10.0, 0.95, 10.0, 0.2),
            create_test_result("img2.png", 50.0, 0.5, 100.0, 1.0),
        ]

        # Initially no composite_score
        assert not hasattr(results[0], "composite_score") or results[0].composite_score is None

        enriched = calculator.enrich_results_with_scores(results)

        # Same list, now with scores
        assert enriched is results
        assert hasattr(results[0], "composite_score")
        assert results[0].composite_score is not None
        assert isinstance(results[0].composite_score, float)


class TestWeightManagement:
    """Test weight configuration management."""

    def test_get_weights(self):
        """Test getting current weights."""
        calculator = CompositeMetricCalculator()

        weights = calculator.get_weights()

        assert weights == DEFAULT_WEIGHTS
        # Should return a copy
        weights["pixel_diff"] = 0.99
        assert calculator.get_weights()["pixel_diff"] == 0.25

    def test_set_weights(self):
        """Test setting new weights."""
        calculator = CompositeMetricCalculator()

        new_weights = {
            "pixel_diff": 0.4,
            "ssim": 0.3,
            "color_distance": 0.2,
            "histogram": 0.1
        }

        calculator.set_weights(new_weights)

        assert calculator.weights == new_weights

    def test_set_weights_validates(self):
        """Test that set_weights validates the new weights."""
        calculator = CompositeMetricCalculator()

        bad_weights = {
            "pixel_diff": 0.5,
            "ssim": 0.5
            # Missing keys
        }

        with pytest.raises(ValueError):
            calculator.set_weights(bad_weights)


class TestSerialization:
    """Test configuration serialization."""

    def test_to_dict(self):
        """Test serializing calculator to dictionary."""
        calculator = CompositeMetricCalculator()

        config = calculator.to_dict()

        assert "weights" in config
        assert "normalization" in config
        assert config["weights"] == DEFAULT_WEIGHTS
        assert config["normalization"] == DEFAULT_NORMALIZATION

    def test_from_dict(self):
        """Test creating calculator from dictionary."""
        custom_config = {
            "weights": {
                "pixel_diff": 0.3,
                "ssim": 0.3,
                "color_distance": 0.2,
                "histogram": 0.2
            },
            "normalization": {
                "pixel_diff_max": 100.0,
                "ssim_min": 0.0,
                "ssim_max": 1.0,
                "color_distance_max": 441.67,
                "histogram_chi_square_max": 2.0
            }
        }

        calculator = CompositeMetricCalculator.from_dict(custom_config)

        assert calculator.weights == custom_config["weights"]
        assert calculator.normalization == custom_config["normalization"]

    def test_round_trip_serialization(self):
        """Test that to_dict() and from_dict() round-trip correctly."""
        original = CompositeMetricCalculator(
            weights={
                "pixel_diff": 0.35,
                "ssim": 0.35,
                "color_distance": 0.2,
                "histogram": 0.1
            }
        )

        config = original.to_dict()
        restored = CompositeMetricCalculator.from_dict(config)

        assert restored.weights == original.weights
        assert restored.normalization == original.normalization


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_metrics_category(self):
        """Test handling of missing metrics category."""
        calculator = CompositeMetricCalculator()

        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/test/new.png"),
            known_good_path=Path("/test/known.png"),
            diff_image_path=Path("/test/diff.png"),
            annotated_image_path=Path("/test/annotated.png"),
            metrics={},  # Empty metrics
            percent_different=0.0,
            histogram_data="",
        )

        # Should not raise, should use defaults
        score = calculator.calculate_composite_score(result)

        # With all defaults (no difference), score should be low
        assert score < 5.0

    def test_partial_histogram_metrics(self):
        """Test handling when only some histogram channels are present."""
        calculator = CompositeMetricCalculator()

        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/test/new.png"),
            known_good_path=Path("/test/known.png"),
            diff_image_path=Path("/test/diff.png"),
            annotated_image_path=Path("/test/annotated.png"),
            metrics={
                "Pixel Difference": {"percent_different": 10.0},
                "Structural Similarity": {"ssim_score": 0.9},
                "Color Difference": {"mean_color_distance": 20.0},
                "Histogram Analysis": {
                    "red_histogram_chi_square": 0.5,
                    # Missing green and blue
                },
            },
            percent_different=10.0,
            histogram_data="",
        )

        # Should handle partial histogram data gracefully
        score = calculator.calculate_composite_score(result)

        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
