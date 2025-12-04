"""
Integration tests for history configuration.

Tests Config dataclass with history fields and CLI argument parsing.
"""

import pytest
import tempfile
from pathlib import Path

from ImageComparisonSystem.config import Config


class TestConfigHistoryFields:
    """Test Config dataclass with history fields."""

    def test_config_with_default_history_settings(self):
        """Test Config with default history settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good"
            )

            # Default values should be set
            assert config.enable_history is True
            assert config.build_number is None
            assert config.history_db_path is None
            assert config.composite_metric_weights is None
            assert config.anomaly_threshold == 2.0
            assert config.retention_keep_all is True
            assert config.retention_max_runs is None
            assert config.retention_max_age_days is None

    def test_config_with_custom_history_settings(self):
        """Test Config with custom history settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_db_path = Path(tmpdir) / "custom_history.db"
            custom_weights = {
                "pixel_diff": 0.3,
                "ssim": 0.3,
                "color_distance": 0.2,
                "histogram": 0.2
            }

            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                enable_history=True,
                build_number="build-12345",
                history_db_path=custom_db_path,
                composite_metric_weights=custom_weights,
                anomaly_threshold=2.5,
                retention_keep_all=False,
                retention_max_runs=100,
                retention_max_age_days=90
            )

            assert config.enable_history is True
            assert config.build_number == "build-12345"
            assert config.history_db_path == custom_db_path
            assert config.composite_metric_weights == custom_weights
            assert config.anomaly_threshold == 2.5
            assert config.retention_keep_all is False
            assert config.retention_max_runs == 100
            assert config.retention_max_age_days == 90

    def test_config_with_history_disabled(self):
        """Test Config with history explicitly disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                enable_history=False
            )

            assert config.enable_history is False

    def test_config_history_db_path_string_conversion(self):
        """Test that history_db_path string is converted to Path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path_str = str(Path(tmpdir) / "test.db")

            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                history_db_path=db_path_str
            )

            # Should be converted to Path in __post_init__
            assert isinstance(config.history_db_path, Path)
            assert str(config.history_db_path) == db_path_str

    def test_config_backward_compatibility(self):
        """Test that Config works without history fields (backward compatibility)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config without any history fields
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                diff_dir="diffs",
                html_dir="reports",
                pixel_diff_threshold=0.01,
                ssim_threshold=0.95
            )

            # Should have default history values
            assert config.enable_history is True
            assert config.build_number is None


class TestConfigValidation:
    """Test that history fields don't break existing validation."""

    def test_validate_with_history_enabled(self):
        """Test that validation works with history enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            new_dir = base_dir / "new"
            known_good_dir = base_dir / "known_good"

            # Create directories with files
            new_dir.mkdir()
            known_good_dir.mkdir()
            (new_dir / "test.png").touch()
            (known_good_dir / "test.png").touch()

            config = Config(
                base_dir=base_dir,
                new_dir="new",
                known_good_dir="known_good",
                enable_history=True,
                build_number="test-build"
            )

            is_valid, message = config.validate()
            assert is_valid is True
            assert message == ""


class TestCompositeMetricWeights:
    """Test composite metric weights configuration."""

    def test_custom_weights_validation(self):
        """Test that custom weights can be set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            weights = {
                "pixel_diff": 0.4,
                "ssim": 0.3,
                "color_distance": 0.2,
                "histogram": 0.1
            }

            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                composite_metric_weights=weights
            )

            assert config.composite_metric_weights == weights
            # Verify sum is 1.0 (this would be validated by composite_metric.py in Phase 4)
            assert abs(sum(weights.values()) - 1.0) < 0.001

    def test_weights_none_uses_defaults(self):
        """Test that None weights will use defaults (validated in Phase 4)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                composite_metric_weights=None
            )

            assert config.composite_metric_weights is None


class TestRetentionPolicySettings:
    """Test retention policy configuration."""

    def test_unlimited_retention(self):
        """Test unlimited retention (default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good"
            )

            assert config.retention_keep_all is True
            assert config.retention_max_runs is None
            assert config.retention_max_age_days is None

    def test_limited_retention_by_count(self):
        """Test retention limited by run count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                retention_keep_all=False,
                retention_max_runs=50
            )

            assert config.retention_keep_all is False
            assert config.retention_max_runs == 50

    def test_limited_retention_by_age(self):
        """Test retention limited by age."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                retention_keep_all=False,
                retention_max_age_days=30
            )

            assert config.retention_keep_all is False
            assert config.retention_max_age_days == 30


class TestAnomalyThreshold:
    """Test anomaly threshold configuration."""

    def test_default_anomaly_threshold(self):
        """Test default anomaly threshold (2.0 std devs)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good"
            )

            assert config.anomaly_threshold == 2.0

    def test_custom_anomaly_threshold(self):
        """Test custom anomaly threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                base_dir=Path(tmpdir),
                new_dir="new",
                known_good_dir="known_good",
                anomaly_threshold=3.0
            )

            assert config.anomaly_threshold == 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
