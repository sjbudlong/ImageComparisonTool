"""
Unit tests for statistical analysis engine.

Tests historical statistics calculation, anomaly detection, and trend analysis.
"""

import pytest
from pathlib import Path

from ImageComparisonSystem.history.statistics import StatisticsCalculator
from ImageComparisonSystem.models import ComparisonResult


def create_test_result_with_score(filename: str, composite_score: float) -> ComparisonResult:
    """Helper to create a test ComparisonResult with composite score."""
    result = ComparisonResult(
        filename=filename,
        new_image_path=Path("/test/new") / filename,
        known_good_path=Path("/test/known") / filename,
        diff_image_path=Path("/test/diff") / filename,
        annotated_image_path=Path("/test/annotated") / filename,
        metrics={},
        percent_different=0.0,
        histogram_data="",
    )
    result.composite_score = composite_score
    return result


class TestStatisticsCalculatorInitialization:
    """Test StatisticsCalculator initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        calculator = StatisticsCalculator()

        assert calculator.anomaly_threshold == 2.0
        assert calculator.min_runs_for_stats == 3

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        calculator = StatisticsCalculator(anomaly_threshold=2.5, min_runs_for_stats=5)

        assert calculator.anomaly_threshold == 2.5
        assert calculator.min_runs_for_stats == 5


class TestHistoricalStatsCalculation:
    """Test calculate_historical_stats() method."""

    def test_calculate_stats_with_sufficient_data(self):
        """Test calculating stats with sufficient historical data."""
        calculator = StatisticsCalculator(min_runs_for_stats=3)
        scores = [10.0, 12.0, 11.0, 13.0, 10.5]

        stats = calculator.calculate_historical_stats(scores)

        assert stats is not None
        mean, std_dev = stats
        assert abs(mean - 11.3) < 0.1  # Mean of [10, 12, 11, 13, 10.5]
        assert std_dev > 0  # Should have non-zero std dev

    def test_calculate_stats_insufficient_data(self):
        """Test that insufficient data returns None."""
        calculator = StatisticsCalculator(min_runs_for_stats=3)
        scores = [10.0, 12.0]  # Only 2 scores, need 3

        stats = calculator.calculate_historical_stats(scores)

        assert stats is None

    def test_calculate_stats_empty_list(self):
        """Test handling of empty scores list."""
        calculator = StatisticsCalculator()
        scores = []

        stats = calculator.calculate_historical_stats(scores)

        assert stats is None

    def test_calculate_stats_single_value(self):
        """Test stats with single value."""
        calculator = StatisticsCalculator(min_runs_for_stats=1)
        scores = [15.0]

        stats = calculator.calculate_historical_stats(scores)

        assert stats is not None
        mean, std_dev = stats
        assert mean == 15.0
        assert std_dev == 0.0  # No variation with single value


class TestAnomalyDetection:
    """Test detect_anomaly() method."""

    def test_detect_no_anomaly_within_threshold(self):
        """Test that values within threshold are not anomalies."""
        calculator = StatisticsCalculator(anomaly_threshold=2.0)

        # Score within 2 std devs
        is_anomaly, deviation = calculator.detect_anomaly(
            current_score=11.0,
            historical_mean=10.0,
            historical_std_dev=1.0
        )

        assert is_anomaly is False
        assert abs(deviation - 1.0) < 0.01  # 1 std dev away

    def test_detect_anomaly_above_threshold(self):
        """Test that values outside threshold are anomalies."""
        calculator = StatisticsCalculator(anomaly_threshold=2.0)

        # Score 2.5 std devs away (exceeds threshold of 2.0)
        is_anomaly, deviation = calculator.detect_anomaly(
            current_score=12.5,
            historical_mean=10.0,
            historical_std_dev=1.0
        )

        assert is_anomaly is True
        assert abs(deviation - 2.5) < 0.01

    def test_detect_anomaly_negative_deviation(self):
        """Test anomaly detection for scores below mean."""
        calculator = StatisticsCalculator(anomaly_threshold=2.0)

        # Score 3 std devs below mean
        is_anomaly, deviation = calculator.detect_anomaly(
            current_score=7.0,
            historical_mean=10.0,
            historical_std_dev=1.0
        )

        assert is_anomaly is True
        assert abs(deviation - (-3.0)) < 0.01  # Negative deviation

    def test_detect_anomaly_zero_std_dev_same_value(self):
        """Test handling of zero std dev when current equals mean."""
        calculator = StatisticsCalculator()

        is_anomaly, deviation = calculator.detect_anomaly(
            current_score=10.0,
            historical_mean=10.0,
            historical_std_dev=0.0  # All historical values identical
        )

        assert is_anomaly is False
        assert deviation == 0.0

    def test_detect_anomaly_zero_std_dev_different_value(self):
        """Test handling of zero std dev when current differs from mean."""
        calculator = StatisticsCalculator()

        is_anomaly, deviation = calculator.detect_anomaly(
            current_score=15.0,
            historical_mean=10.0,
            historical_std_dev=0.0
        )

        assert is_anomaly is True
        assert deviation == float('inf')  # Infinite deviation


class TestEnrichResultWithStatistics:
    """Test enrich_result_with_statistics() method."""

    def test_enrich_with_sufficient_history(self):
        """Test enriching result with sufficient historical data."""
        calculator = StatisticsCalculator(min_runs_for_stats=3)
        result = create_test_result_with_score("test.png", 15.0)
        historical_scores = [10.0, 11.0, 12.0, 11.5, 10.5]

        enriched = calculator.enrich_result_with_statistics(result, historical_scores)

        assert enriched is result  # Same object
        assert enriched.historical_mean is not None
        assert enriched.historical_std_dev is not None
        assert enriched.std_dev_from_mean is not None
        assert enriched.is_anomaly is True  # 15.0 is significantly higher than ~11.0

    def test_enrich_with_insufficient_history(self):
        """Test enriching result with insufficient historical data."""
        calculator = StatisticsCalculator(min_runs_for_stats=5)
        result = create_test_result_with_score("test.png", 15.0)
        historical_scores = [10.0, 11.0]  # Only 2 scores, need 5

        enriched = calculator.enrich_result_with_statistics(result, historical_scores)

        assert enriched.historical_mean is None
        assert enriched.historical_std_dev is None
        assert enriched.std_dev_from_mean is None
        assert enriched.is_anomaly is False

    def test_enrich_without_composite_score(self):
        """Test handling result without composite_score."""
        calculator = StatisticsCalculator()
        result = create_test_result_with_score("test.png", None)  # No score
        result.composite_score = None
        historical_scores = [10.0, 11.0, 12.0]

        enriched = calculator.enrich_result_with_statistics(result, historical_scores)

        # Should return unchanged
        assert enriched is result


class TestBatchEnrichment:
    """Test enrich_results_batch() method."""

    def test_enrich_batch(self):
        """Test enriching multiple results."""
        calculator = StatisticsCalculator(min_runs_for_stats=3)

        results = [
            create_test_result_with_score("img1.png", 10.5),
            create_test_result_with_score("img2.png", 50.0),
            create_test_result_with_score("img3.png", 12.0),
        ]

        historical_data = {
            "img1.png": [10.0, 11.0, 10.5, 11.5],  # Similar history
            "img2.png": [10.0, 11.0, 12.0, 11.5],  # Very different (50.0 vs ~11.0)
            "img3.png": [11.0, 12.0, 11.5],        # Similar history
        }

        enriched = calculator.enrich_results_batch(results, historical_data)

        assert enriched is results
        assert results[0].is_anomaly is False  # Close to history
        assert results[1].is_anomaly is True   # Far from history
        assert results[2].is_anomaly is False  # Close to history


class TestAnomalySummary:
    """Test get_anomaly_summary() method."""

    def test_get_summary(self):
        """Test generating anomaly summary."""
        calculator = StatisticsCalculator()

        results = [
            create_test_result_with_score("img1.png", 10.0),
            create_test_result_with_score("img2.png", 50.0),
            create_test_result_with_score("img3.png", 12.0),
        ]

        # Enrich results
        results[0].historical_mean = 10.0
        results[0].historical_std_dev = 1.0
        results[0].std_dev_from_mean = 0.0
        results[0].is_anomaly = False

        results[1].historical_mean = 10.0
        results[1].historical_std_dev = 1.0
        results[1].std_dev_from_mean = 40.0
        results[1].is_anomaly = True

        results[2].historical_mean = 12.0
        results[2].historical_std_dev = 1.0
        results[2].std_dev_from_mean = 0.0
        results[2].is_anomaly = False

        summary = calculator.get_anomaly_summary(results)

        assert summary["total_results"] == 3
        assert summary["results_with_statistics"] == 3
        assert summary["total_anomalies"] == 1
        assert summary["anomaly_rate"] == pytest.approx(1/3)
        assert len(summary["top_deviations"]) > 0


class TestFilterAnomalies:
    """Test filter_anomalies() method."""

    def test_filter_anomalies_only(self):
        """Test filtering to get only anomalies."""
        calculator = StatisticsCalculator()

        results = [
            create_test_result_with_score("img1.png", 10.0),
            create_test_result_with_score("img2.png", 50.0),
            create_test_result_with_score("img3.png", 12.0),
        ]

        results[0].is_anomaly = False
        results[1].is_anomaly = True
        results[2].is_anomaly = False

        anomalies = calculator.filter_anomalies(results, include_non_anomalies=False)

        assert len(anomalies) == 1
        assert anomalies[0].filename == "img2.png"

    def test_filter_non_anomalies_only(self):
        """Test filtering to get only non-anomalies."""
        calculator = StatisticsCalculator()

        results = [
            create_test_result_with_score("img1.png", 10.0),
            create_test_result_with_score("img2.png", 50.0),
            create_test_result_with_score("img3.png", 12.0),
        ]

        results[0].is_anomaly = False
        results[1].is_anomaly = True
        results[2].is_anomaly = False

        non_anomalies = calculator.filter_anomalies(results, include_non_anomalies=True)

        assert len(non_anomalies) == 2
        assert non_anomalies[0].filename == "img1.png"
        assert non_anomalies[1].filename == "img3.png"


class TestTrendDirection:
    """Test get_trend_direction() method."""

    def test_trend_increasing(self):
        """Test detecting increasing trend."""
        calculator = StatisticsCalculator()
        scores = [10.0, 15.0, 20.0, 25.0, 30.0]

        trend = calculator.get_trend_direction(scores)

        assert trend == "increasing"

    def test_trend_decreasing(self):
        """Test detecting decreasing trend."""
        calculator = StatisticsCalculator()
        scores = [30.0, 25.0, 20.0, 15.0, 10.0]

        trend = calculator.get_trend_direction(scores)

        assert trend == "decreasing"

    def test_trend_stable(self):
        """Test detecting stable trend."""
        calculator = StatisticsCalculator()
        scores = [10.0, 10.5, 10.2, 10.3, 10.1]

        trend = calculator.get_trend_direction(scores)

        assert trend == "stable"

    def test_trend_insufficient_data(self):
        """Test that insufficient data returns None."""
        calculator = StatisticsCalculator()
        scores = [10.0, 12.0]  # Only 2 values, need 3

        trend = calculator.get_trend_direction(scores, min_samples=3)

        assert trend is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_all_identical_historical_scores(self):
        """Test handling when all historical scores are identical."""
        calculator = StatisticsCalculator()
        result = create_test_result_with_score("test.png", 10.0)
        historical_scores = [10.0, 10.0, 10.0, 10.0]

        enriched = calculator.enrich_result_with_statistics(result, historical_scores)

        assert enriched.historical_mean == 10.0
        assert enriched.historical_std_dev == 0.0
        assert enriched.is_anomaly is False  # Same as all historical

    def test_current_score_very_different(self):
        """Test handling of current score vastly different from history."""
        calculator = StatisticsCalculator(anomaly_threshold=2.0)
        result = create_test_result_with_score("test.png", 1000.0)
        historical_scores = [10.0, 11.0, 10.5, 11.5]

        enriched = calculator.enrich_result_with_statistics(result, historical_scores)

        assert enriched.is_anomaly is True
        assert abs(enriched.std_dev_from_mean) > 10  # Very high deviation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
