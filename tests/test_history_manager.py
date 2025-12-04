"""
Unit tests for history.history_manager module.

Tests saving runs, querying historical data, and enrichment functionality.
"""

import pytest
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from ImageComparisonSystem.history.history_manager import HistoryManager
from ImageComparisonSystem.models import ComparisonResult


# Mock Config class for testing
@dataclass
class MockConfig:
    """Mock configuration for testing."""

    base_dir: Path
    new_dir: str = "new"
    known_good_dir: str = "known_good"
    history_db_path: Optional[Path] = None
    build_number: Optional[str] = None
    pixel_diff_threshold: float = 0.01
    ssim_threshold: float = 0.95
    color_distance_threshold: float = 10.0
    use_histogram_equalization: bool = False
    diff_enhancement_factor: float = 5.0

    @property
    def new_path(self) -> Path:
        return self.base_dir / self.new_dir


def create_mock_result(
    filename: str, percent_diff: float, subdirectory: str = ""
) -> ComparisonResult:
    """Create a mock ComparisonResult for testing."""
    base_path = Path("/test/base")
    new_path = (
        base_path / "new" / subdirectory / filename
        if subdirectory
        else base_path / "new" / filename
    )
    known_path = (
        base_path / "known_good" / subdirectory / filename
        if subdirectory
        else base_path / "known_good" / filename
    )

    return ComparisonResult(
        filename=filename,
        new_image_path=new_path,
        known_good_path=known_path,
        diff_image_path=Path("/test/diff") / filename,
        annotated_image_path=Path("/test/annotated") / filename,
        metrics={
            "Pixel Difference": {
                "percent_different": percent_diff,
                "changed_pixels": 1000,
                "mean_absolute_error": 5.5,
                "max_difference": 255,
            },
            "Structural Similarity": {
                "ssim_score": 0.95,
                "ssim_percentage": 5.0,
            },
            "Color Difference": {
                "mean_color_distance": 8.5,
                "max_color_distance": 150.0,
                "significant_color_changes": 500,
            },
            "Histogram Analysis": {
                "red_histogram_correlation": 0.98,
                "green_histogram_correlation": 0.97,
                "blue_histogram_correlation": 0.99,
                "red_histogram_chi_square": 0.5,
                "green_histogram_chi_square": 0.6,
                "blue_histogram_chi_square": 0.4,
            },
        },
        percent_different=percent_diff,
        histogram_data="base64_encoded_data",
    )


@pytest.fixture
def temp_history_manager():
    """Create a temporary HistoryManager for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        config = MockConfig(base_dir=base_dir, build_number="test-build-001")
        manager = HistoryManager(config)
        yield manager
        manager.close()


class TestHistoryManagerInitialization:
    """Test HistoryManager initialization."""

    def test_init_with_default_path(self):
        """Test initialization with default database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            config = MockConfig(base_dir=base_dir)
            manager = HistoryManager(config)

            expected_path = base_dir / ".imgcomp_history" / "comparison_history.db"
            assert manager.db_path == expected_path
            assert manager.db_path.exists()
            manager.close()

    def test_init_with_custom_path(self):
        """Test initialization with custom database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            custom_db_path = Path(tmpdir) / "custom" / "history.db"
            config = MockConfig(base_dir=base_dir, history_db_path=custom_db_path)
            manager = HistoryManager(config)

            assert manager.db_path == custom_db_path
            assert manager.db_path.exists()
            manager.close()


class TestSaveRun:
    """Test saving runs and results."""

    def test_save_empty_run(self, temp_history_manager):
        """Test saving a run with no results."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-100")

        run_id = temp_history_manager.save_run([], config)

        assert run_id > 0

        # Verify run was saved
        run = temp_history_manager.get_run(run_id)
        assert run is not None
        assert run["build_number"] == "build-100"
        assert run["total_images"] == 0
        assert run["avg_difference"] == 0.0

    def test_save_run_with_results(self, temp_history_manager):
        """Test saving a run with multiple results."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-200")

        results = [
            create_mock_result("image1.png", 10.5),
            create_mock_result("image2.png", 25.3),
            create_mock_result("image3.png", 5.1),
        ]

        run_id = temp_history_manager.save_run(results, config, notes="Test run")

        assert run_id > 0

        # Verify run metadata
        run = temp_history_manager.get_run(run_id)
        assert run["build_number"] == "build-200"
        assert run["total_images"] == 3
        assert abs(run["avg_difference"] - 13.63) < 0.1  # (10.5 + 25.3 + 5.1) / 3
        assert run["max_difference"] == 25.3
        assert run["notes"] == "Test run"

        # Verify results were saved
        saved_results = temp_history_manager.get_results_for_run(run_id)
        assert len(saved_results) == 3

    def test_save_run_with_subdirectories(self, temp_history_manager):
        """Test saving results with subdirectory grouping."""
        config = MockConfig(base_dir=Path("/test/base"), build_number="build-300")

        results = [
            create_mock_result("image1.png", 10.0, "renders/scene1"),
            create_mock_result("image2.png", 20.0, "renders/scene2"),
        ]

        run_id = temp_history_manager.save_run(results, config)

        # Verify subdirectories are saved
        saved_results = temp_history_manager.get_results_for_run(run_id)
        assert saved_results[0]["subdirectory"] in ["renders/scene1", "renders/scene2"]
        assert saved_results[1]["subdirectory"] in ["renders/scene1", "renders/scene2"]


class TestQueryRuns:
    """Test querying runs."""

    def test_get_run_by_id(self, temp_history_manager):
        """Test retrieving a run by ID."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-400")
        run_id = temp_history_manager.save_run([], config)

        run = temp_history_manager.get_run(run_id)

        assert run is not None
        assert run["run_id"] == run_id
        assert run["build_number"] == "build-400"

    def test_get_nonexistent_run(self, temp_history_manager):
        """Test retrieving a non-existent run."""
        run = temp_history_manager.get_run(99999)
        assert run is None

    def test_get_run_by_build_number(self, temp_history_manager):
        """Test retrieving a run by build number."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-500")
        run_id = temp_history_manager.save_run([], config)

        run = temp_history_manager.get_run_by_build_number("build-500")

        assert run is not None
        assert run["run_id"] == run_id
        assert run["build_number"] == "build-500"

    def test_get_all_runs(self, temp_history_manager):
        """Test retrieving all runs."""
        config1 = MockConfig(base_dir=Path("/test"), build_number="build-600")
        config2 = MockConfig(base_dir=Path("/test"), build_number="build-700")

        temp_history_manager.save_run([], config1)
        temp_history_manager.save_run([], config2)

        runs = temp_history_manager.get_all_runs(limit=10)

        assert len(runs) >= 2
        # Most recent first
        assert runs[0]["build_number"] == "build-700"
        assert runs[1]["build_number"] == "build-600"


class TestQueryResults:
    """Test querying results."""

    def test_get_results_for_run(self, temp_history_manager):
        """Test retrieving results for a specific run."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-800")
        results = [
            create_mock_result("image1.png", 50.0),
            create_mock_result("image2.png", 10.0),
            create_mock_result("image3.png", 30.0),
        ]

        run_id = temp_history_manager.save_run(results, config)

        saved_results = temp_history_manager.get_results_for_run(run_id)

        assert len(saved_results) == 3
        # Should be sorted by composite_score DESC (though composite_score is None here)
        assert all("filename" in r for r in saved_results)

    def test_get_history_for_image(self, temp_history_manager):
        """Test retrieving historical results for a specific image."""
        config1 = MockConfig(base_dir=Path("/test"), build_number="build-900")
        config2 = MockConfig(base_dir=Path("/test"), build_number="build-901")

        # Save two runs with the same image
        results1 = [create_mock_result("test_image.png", 10.0)]
        results2 = [create_mock_result("test_image.png", 20.0)]

        temp_history_manager.save_run(results1, config1)
        temp_history_manager.save_run(results2, config2)

        history = temp_history_manager.get_history_for_image("test_image.png")

        assert len(history) == 2
        # Most recent first
        assert history[0]["build_number"] == "build-901"
        assert history[1]["build_number"] == "build-900"

    def test_get_history_for_image_with_subdirectory(self, temp_history_manager):
        """Test retrieving history with subdirectory filter."""
        config = MockConfig(base_dir=Path("/test/base"), build_number="build-1000")

        results = [
            create_mock_result("image.png", 10.0, "renders/scene1"),
            create_mock_result("image.png", 20.0, "renders/scene2"),
        ]

        temp_history_manager.save_run(results, config)

        history = temp_history_manager.get_history_for_image(
            "image.png", subdirectory="renders/scene1"
        )

        assert len(history) == 1
        assert history[0]["subdirectory"] == "renders/scene1"


class TestDeleteRun:
    """Test deleting runs."""

    def test_delete_run(self, temp_history_manager):
        """Test deleting a run."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-1100")
        results = [create_mock_result("image1.png", 10.0)]

        run_id = temp_history_manager.save_run(results, config)

        # Verify run and results exist
        assert temp_history_manager.get_run(run_id) is not None
        assert len(temp_history_manager.get_results_for_run(run_id)) == 1

        # Delete run
        success = temp_history_manager.delete_run(run_id)
        assert success is True

        # Verify run and results are gone (CASCADE DELETE)
        assert temp_history_manager.get_run(run_id) is None
        assert len(temp_history_manager.get_results_for_run(run_id)) == 0

    def test_delete_nonexistent_run(self, temp_history_manager):
        """Test deleting a non-existent run."""
        success = temp_history_manager.delete_run(99999)
        assert success is False


class TestStatistics:
    """Test statistical methods."""

    def test_get_total_run_count(self, temp_history_manager):
        """Test getting total run count."""
        config1 = MockConfig(base_dir=Path("/test"), build_number="build-1200")
        config2 = MockConfig(base_dir=Path("/test"), build_number="build-1201")

        temp_history_manager.save_run([], config1)
        temp_history_manager.save_run([], config2)

        count = temp_history_manager.get_total_run_count()
        assert count == 2

    def test_get_total_result_count(self, temp_history_manager):
        """Test getting total result count."""
        config = MockConfig(base_dir=Path("/test"), build_number="build-1300")
        results = [
            create_mock_result("image1.png", 10.0),
            create_mock_result("image2.png", 20.0),
            create_mock_result("image3.png", 30.0),
        ]

        temp_history_manager.save_run(results, config)

        count = temp_history_manager.get_total_result_count()
        assert count == 3

    def test_get_recent_runs_for_image(self, temp_history_manager):
        """Test getting recent runs for trend analysis."""
        # Save multiple runs with composite scores
        for i in range(5):
            config = MockConfig(
                base_dir=Path("/test"), build_number=f"build-{1400 + i}"
            )
            result = create_mock_result("trend_image.png", 10.0 + i * 5)
            result.composite_score = 50.0 + i * 10  # Add composite score

            temp_history_manager.save_run([result], config)

        trends = temp_history_manager.get_recent_runs_for_image(
            "trend_image.png", count=3
        )

        assert len(trends) == 3
        # Should return (timestamp, composite_score) tuples
        assert all(len(t) == 2 for t in trends)
        assert all(isinstance(t[1], float) for t in trends)


class TestEnrichWithHistory:
    """Test enrichment functionality."""

    def test_enrich_with_history_placeholder(self, temp_history_manager):
        """Test that enrich_with_history placeholder returns results unchanged."""
        results = [
            create_mock_result("image1.png", 10.0),
            create_mock_result("image2.png", 20.0),
        ]

        enriched = temp_history_manager.enrich_with_history(results)

        # For now, should return unchanged (full implementation in Phase 5)
        assert enriched == results
        assert len(enriched) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
