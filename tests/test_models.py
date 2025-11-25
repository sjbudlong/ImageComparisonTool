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
            histogram_data="base64_encoded_data"
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
            histogram_data="base64_data"
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
            histogram_data="data"
        )
        
        result_dict = result.to_dict()
        assert result_dict["metrics"] == metrics
    
    def test_comparison_result_with_complex_metrics(self):
        """ComparisonResult should handle complex nested metrics."""
        metrics = {
            "ssim": 0.95,
            "pixel_diff": {"count": 150, "percentage": 1.2},
            "channel_diff": {"r": 5, "g": 3, "b": 2},
            "histogram_correlation": [0.98, 0.97, 0.96]
        }
        result = ComparisonResult(
            filename="complex.png",
            new_image_path=Path("/new.png"),
            known_good_path=Path("/known.png"),
            diff_image_path=Path("/diff.png"),
            annotated_image_path=Path("/annotated.png"),
            metrics=metrics,
            percent_different=1.2,
            histogram_data="data"
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
            histogram_data=""
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
            histogram_data=""
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
            histogram_data=""
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
            histogram_data="data"
        )

        result_dict = result.to_dict(base_path)
        assert "subdirectory" in result_dict
        assert result_dict["subdirectory"] == "ui"
