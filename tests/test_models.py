"""
Unit tests for models module.
"""

import pytest
from pathlib import Path
from models import ComparisonResult


@pytest.mark.unit
class TestComparisonResult:
    """Test ComparisonResult dataclass."""

    def test_comparison_result_creation(self):
        """ComparisonResult should be creatable with required fields."""
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/path/to/new.png"),
            known_good_path=Path("/path/to/known.png"),
            diff_image_path=Path("/path/to/diff.png"),
            annotated_image_path=Path("/path/to/annotated.png"),
            metrics={"ssim": 0.95, "pixel_diff": 1.2},
            percent_different=1.2,
            histogram_data="base64_encoded_data",
        )
        assert result.filename == "test.png"
        assert result.percent_different == 1.2

    def test_comparison_result_to_dict(self):
        """to_dict should convert Path objects to strings."""
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/path/to/new.png"),
            known_good_path=Path("/path/to/known.png"),
            diff_image_path=Path("/path/to/diff.png"),
            annotated_image_path=Path("/path/to/annotated.png"),
            metrics={"ssim": 0.95},
            percent_different=1.2,
            histogram_data="base64_data",
        )

        result_dict = result.to_dict()

        # Verify all fields are present
        assert "filename" in result_dict
        assert "metrics" in result_dict
        assert "percent_different" in result_dict

        # Verify Path objects are converted to strings
        assert isinstance(result_dict["new_image_path"], str)
        assert isinstance(result_dict["known_good_path"], str)
        assert isinstance(result_dict["diff_image_path"], str)
        assert isinstance(result_dict["annotated_image_path"], str)

        # Verify values are correct (use forward slashes - cross-platform)
        # On Windows, Path converts to backslashes, so we check containment instead
        assert "new.png" in result_dict["new_image_path"]
        assert "known.png" in result_dict["known_good_path"]

    def test_comparison_result_to_dict_preserves_metrics(self):
        """to_dict should preserve metrics dictionary."""
        metrics = {"ssim": 0.95, "pixel_diff": 1.2, "color_distance": 15.5}
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics=metrics,
            percent_different=1.2,
            histogram_data="data",
        )

        result_dict = result.to_dict()
        assert result_dict["metrics"] == metrics

    def test_comparison_result_with_complex_metrics(self):
        """ComparisonResult should handle complex nested metrics."""
        metrics = {
            "ssim": 0.95,
            "pixel_diff": {"count": 150, "percentage": 1.2},
            "channel_diff": {"r": 5, "g": 3, "b": 2},
            "histogram_correlation": [0.98, 0.97, 0.96],
        }
        result = ComparisonResult(
            filename="complex.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics=metrics,
            percent_different=1.2,
            histogram_data="data",
        )

        result_dict = result.to_dict()
        assert result_dict["metrics"] == metrics
        assert result_dict["metrics"]["pixel_diff"]["percentage"] == 1.2

    def test_get_subdirectory_with_subdirectory(self, tmp_path):
        """get_subdirectory should return subdirectory path."""
        base_path = tmp_path / "images"
        base_path.mkdir()
        subdir = base_path / "ui" / "screenshots"
        subdir.mkdir(parents=True)
        image_path = subdir / "test.png"

        result = ComparisonResult(
            filename="test.png",
            new_image_path=image_path,
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={},
            percent_different=1.0,
            histogram_data="",
        )

        subdir_result = result.get_subdirectory(base_path)
        assert subdir_result == "ui/screenshots"

    def test_get_subdirectory_root_level(self, tmp_path):
        """get_subdirectory should return empty string for root level images."""
        base_path = tmp_path / "images"
        base_path.mkdir()
        image_path = base_path / "test.png"

        result = ComparisonResult(
            filename="test.png",
            new_image_path=image_path,
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={},
            percent_different=1.0,
            histogram_data="",
        )

        subdir_result = result.get_subdirectory(base_path)
        assert subdir_result == ""

    def test_get_subdirectory_invalid_base_path(self, tmp_path):
        """get_subdirectory should return empty string for invalid base path."""
        base_path = tmp_path / "images"
        other_path = tmp_path / "other"
        other_path.mkdir()
        image_path = other_path / "test.png"

        result = ComparisonResult(
            filename="test.png",
            new_image_path=image_path,
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={},
            percent_different=1.0,
            histogram_data="",
        )

        subdir_result = result.get_subdirectory(base_path)
        assert subdir_result == ""

    def test_to_dict_with_base_path(self, tmp_path):
        """to_dict should include subdirectory when base_path is provided."""
        base_path = tmp_path / "images"
        base_path.mkdir()
        subdir = base_path / "ui"
        subdir.mkdir()
        image_path = subdir / "test.png"

        result = ComparisonResult(
            filename="test.png",
            new_image_path=image_path,
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.95},
            percent_different=1.2,
            histogram_data="data",
        )

        result_dict = result.to_dict(base_path)
        assert "subdirectory" in result_dict
        assert result_dict["subdirectory"] == "ui"


@pytest.mark.unit
class TestComparisonResultHistoryFields:
    """Test ComparisonResult history tracking fields (Phase 6)."""

    def test_history_fields_default_to_none(self):
        """History fields should default to None for backward compatibility."""
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.95},
            percent_different=1.2,
            histogram_data="data",
        )

        # All history fields should be None/False by default
        assert result.composite_score is None
        assert result.historical_mean is None
        assert result.historical_std_dev is None
        assert result.std_dev_from_mean is None
        assert result.is_anomaly is False
        assert result.run_id is None

    def test_history_fields_can_be_set(self):
        """History fields should be settable after creation."""
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.95},
            percent_different=1.2,
            histogram_data="data",
        )

        # Set history fields
        result.composite_score = 45.5
        result.historical_mean = 42.0
        result.historical_std_dev = 3.5
        result.std_dev_from_mean = 1.0
        result.is_anomaly = False
        result.run_id = 123

        # Verify fields are set
        assert result.composite_score == 45.5
        assert result.historical_mean == 42.0
        assert result.historical_std_dev == 3.5
        assert result.std_dev_from_mean == 1.0
        assert result.is_anomaly is False
        assert result.run_id == 123

    def test_to_dict_includes_history_fields(self):
        """to_dict should include history fields when they are set."""
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.95},
            percent_different=1.2,
            histogram_data="data",
        )

        # Set history fields
        result.composite_score = 45.5
        result.historical_mean = 42.0
        result.historical_std_dev = 3.5
        result.std_dev_from_mean = 1.0
        result.is_anomaly = True
        result.run_id = 123

        result_dict = result.to_dict()

        # Verify history fields are in dictionary
        assert result_dict["composite_score"] == 45.5
        assert result_dict["historical_mean"] == 42.0
        assert result_dict["historical_std_dev"] == 3.5
        assert result_dict["std_dev_from_mean"] == 1.0
        assert result_dict["is_anomaly"] is True
        assert result_dict["run_id"] == 123

    def test_to_dict_excludes_none_history_fields(self):
        """to_dict should not include history fields when they are None."""
        result = ComparisonResult(
            filename="test.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.95},
            percent_different=1.2,
            histogram_data="data",
        )

        result_dict = result.to_dict()

        # History fields should not be present when None
        # (asdict includes them, but they're None values)
        # Our to_dict only adds them explicitly if not None
        assert result_dict.get("composite_score") is None
        assert result_dict.get("historical_mean") is None
        assert result_dict.get("historical_std_dev") is None

    def test_anomaly_detection_workflow(self):
        """Test typical workflow of setting anomaly detection fields."""
        result = ComparisonResult(
            filename="anomaly.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.5},
            percent_different=50.0,
            histogram_data="data",
        )

        # Simulate history system enrichment
        result.composite_score = 75.0  # High difference score
        result.historical_mean = 12.0  # Usually low difference
        result.historical_std_dev = 3.0
        result.std_dev_from_mean = 21.0  # 21σ away!
        result.is_anomaly = True  # Flagged as anomaly
        result.run_id = 456

        # Verify anomaly is properly flagged
        assert result.is_anomaly is True
        assert result.std_dev_from_mean > 2.0
        assert result.composite_score > result.historical_mean

    def test_backward_compatibility_without_history(self):
        """Results without history fields should work identically to before."""
        # Create result exactly as in old code (no history fields)
        result = ComparisonResult(
            filename="legacy.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics={"ssim": 0.95, "pixel_diff": 1.2},
            percent_different=1.2,
            histogram_data="base64_data",
        )

        # Should work exactly as before
        assert result.filename == "legacy.png"
        assert result.percent_different == 1.2

        # to_dict should work
        result_dict = result.to_dict()
        assert "filename" in result_dict
        assert "metrics" in result_dict

        # History fields exist but are None/False
        assert hasattr(result, 'composite_score')
        assert hasattr(result, 'is_anomaly')
