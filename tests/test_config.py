"""
Unit tests for config module.
"""

import pytest
import logging
from pathlib import Path
from config import Config, HistogramConfig


# Get logger for this module
logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestConfig:
    """Test Config dataclass."""

    def test_config_creation_with_path_object(self, temp_image_dir):
        """Config should accept Path objects."""
        logger.debug(f"Testing config creation with Path object: {temp_image_dir}")
        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )
        assert isinstance(config.base_dir, Path)
        assert config.new_dir == "new"
        assert config.known_good_dir == "known_good"
        logger.info("✓ Config creation with Path object test passed")

    def test_config_creation_with_string_path(self, temp_image_dir):
        """Config should convert string paths to Path objects."""
        logger.debug(f"Testing config creation with string path: {str(temp_image_dir)}")
        config = Config(
            base_dir=str(temp_image_dir), new_dir="new", known_good_dir="known_good"
        )
        assert isinstance(config.base_dir, Path)
        logger.info("✓ Config creation with string path test passed")

    def test_config_default_values(self, temp_image_dir):
        """Config should have sensible default values."""
        logger.debug("Testing config default values")
        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )
        assert config.diff_dir == "diffs"
        assert config.html_dir == "reports"
        assert config.pixel_diff_threshold == 0.01
        assert config.ssim_threshold == 0.95
        assert config.use_histogram_equalization is True
        assert config.highlight_color == (255, 0, 0)
        logger.info("✓ Config default values test passed")

    def test_config_custom_values(self, temp_image_dir):
        """Config should accept custom threshold values."""
        logger.debug("Testing config custom values")
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            pixel_diff_threshold=0.05,
            ssim_threshold=0.90,
            use_histogram_equalization=False,
            highlight_color=(0, 255, 0),
        )
        assert config.pixel_diff_threshold == 0.05
        assert config.ssim_threshold == 0.90
        assert config.use_histogram_equalization is False
        assert config.highlight_color == (0, 255, 0)
        logger.info("✓ Config custom values test passed")

    def test_config_paths_properties(self, temp_image_dir):
        """Config properties should return correct paths."""
        logger.debug("Testing config path properties")
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            diff_dir="diffs",
            html_dir="reports",
        )
        assert config.new_path == temp_image_dir / "new"
        assert config.known_good_path == temp_image_dir / "known_good"
        assert config.diff_path == temp_image_dir / "diffs"
        assert config.html_path == temp_image_dir / "reports"
        logger.info("✓ Config path properties test passed")

    def test_config_validate_missing_new_dir(self, temp_image_dir):
        """Validation should fail if new directory doesn't exist."""
        logger.debug("Testing validation with missing new directory")
        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )
        is_valid, error_msg = config.validate()
        assert not is_valid
        assert "New images directory" in error_msg
        logger.info("✓ Config validation for missing new dir test passed")

    def test_config_validate_missing_known_good_dir(self, temp_image_dir):
        """Validation should fail if known_good directory doesn't exist."""
        logger.debug("Testing validation with missing known_good directory")
        new_dir = temp_image_dir / "new"
        new_dir.mkdir()

        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )
        is_valid, error_msg = config.validate()
        assert not is_valid
        assert "Known good directory" in error_msg
        logger.info("✓ Config validation for missing known_good dir test passed")

    def test_config_validate_empty_directories(self, temp_image_dir):
        """Validation should fail if directories are empty."""
        logger.debug("Testing validation with empty directories")
        new_dir = temp_image_dir / "new"
        known_good_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_good_dir.mkdir()

        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )
        is_valid, error_msg = config.validate()
        assert not is_valid
        assert "empty" in error_msg.lower()
        logger.info("✓ Config validation for empty directories test passed")

    def test_config_validate_success(self, valid_config):
        """Validation should succeed with valid directories."""
        logger.debug("Testing config validation success")
        is_valid, error_msg = valid_config.validate()
        assert is_valid
        assert error_msg == ""
        logger.info("✓ Config validation success test passed")

    def test_config_base_dir_creation(self, tmp_path):
        """Config should create base_dir if it doesn't exist."""
        logger.debug("Testing config base_dir creation")
        new_base = tmp_path / "does_not_exist" / "nested"
        config = Config(base_dir=new_base, new_dir="new", known_good_dir="known_good")
        assert config.base_dir.exists()
        logger.info("✓ Config base_dir creation test passed")

    def test_config_histogram_config_auto_initialization(self, temp_image_dir):
        """Config should auto-initialize histogram_config with defaults."""
        logger.debug("Testing Config auto-initialization of histogram_config")
        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )

        assert config.histogram_config is not None
        assert isinstance(config.histogram_config, HistogramConfig)
        assert config.histogram_config.bins == 256
        assert config.histogram_config.figure_width == 16
        assert config.histogram_config.show_grayscale is True
        assert config.histogram_config.show_rgb is True

        logger.info("✓ Config histogram_config auto-initialization test passed")

    def test_config_histogram_config_custom(self, temp_image_dir):
        """Config should accept custom HistogramConfig."""
        logger.debug("Testing Config with custom HistogramConfig")
        hist_config = HistogramConfig(
            bins=128,
            figure_width=18,
            figure_height=7,
            show_grayscale=True,
            show_rgb=False,
        )

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            histogram_config=hist_config,
        )

        assert config.histogram_config.bins == 128
        assert config.histogram_config.figure_width == 18
        assert config.histogram_config.figure_height == 7
        assert config.histogram_config.show_grayscale is True
        assert config.histogram_config.show_rgb is False

        logger.info("✓ Config custom HistogramConfig test passed")

    def test_config_flip_defaults(self, temp_image_dir):
        """Config should have correct FLIP default values."""
        logger.debug("Testing Config FLIP default values")
        config = Config(
            base_dir=temp_image_dir, new_dir="new", known_good_dir="known_good"
        )

        # FLIP disabled by default
        assert config.enable_flip is False
        assert config.flip_pixels_per_degree == 67.0
        assert config.flip_colormaps == ["viridis"]
        assert config.flip_default_colormap == "viridis"

        # Visualization toggles default to True
        assert config.show_flip_visualization is True
        assert config.show_ssim_visualization is True
        assert config.show_pixel_diff_visualization is True
        assert config.show_color_distance_visualization is True
        assert config.show_histogram_visualization is True
        assert config.show_dimension_visualization is True

        logger.info("✓ Config FLIP default values test passed")

    def test_config_flip_enabled_custom_values(self, temp_image_dir):
        """Config should accept custom FLIP values when enabled."""
        logger.debug("Testing Config with custom FLIP values")
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True,
            flip_pixels_per_degree=42.0,
            flip_colormaps=["viridis", "jet", "turbo"],
            flip_default_colormap="jet",
        )

        assert config.enable_flip is True
        assert config.flip_pixels_per_degree == 42.0
        assert config.flip_colormaps == ["viridis", "jet", "turbo"]
        assert config.flip_default_colormap == "jet"

        logger.info("✓ Config custom FLIP values test passed")

    def test_config_flip_invalid_colormap_raises_error(self, temp_image_dir):
        """Config should reject invalid FLIP colormaps."""
        logger.debug("Testing Config with invalid FLIP colormap")

        with pytest.raises(ValueError) as exc_info:
            Config(
                base_dir=temp_image_dir,
                new_dir="new",
                known_good_dir="known_good",
                enable_flip=True,
                flip_colormaps=["viridis", "invalid_colormap"],
            )

        assert "Invalid FLIP colormaps" in str(exc_info.value)
        assert "invalid_colormap" in str(exc_info.value)
        logger.info("✓ Config invalid FLIP colormap validation test passed")

    def test_config_flip_default_colormap_not_in_list_raises_error(self, temp_image_dir):
        """Config should reject default colormap not in colormaps list."""
        logger.debug("Testing Config with default colormap not in list")

        with pytest.raises(ValueError) as exc_info:
            Config(
                base_dir=temp_image_dir,
                new_dir="new",
                known_good_dir="known_good",
                enable_flip=True,
                flip_colormaps=["viridis", "jet"],
                flip_default_colormap="turbo",
            )

        assert "flip_default_colormap" in str(exc_info.value)
        assert "must be one of flip_colormaps" in str(exc_info.value)
        logger.info("✓ Config default colormap validation test passed")

    def test_config_flip_validation_skipped_when_disabled(self, temp_image_dir):
        """Config should skip FLIP validation when FLIP is disabled."""
        logger.debug("Testing Config skips FLIP validation when disabled")

        # Should not raise error even with invalid colormap, since FLIP is disabled
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=False,
            flip_colormaps=["invalid_colormap"],  # Invalid but not validated
        )

        assert config.enable_flip is False
        logger.info("✓ Config FLIP validation skipped when disabled test passed")

    def test_config_visualization_toggles_custom(self, temp_image_dir):
        """Config should accept custom visualization toggle values."""
        logger.debug("Testing Config with custom visualization toggles")
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            show_flip_visualization=False,
            show_ssim_visualization=False,
            show_pixel_diff_visualization=True,
            show_color_distance_visualization=False,
            show_histogram_visualization=True,
            show_dimension_visualization=False,
        )

        assert config.show_flip_visualization is False
        assert config.show_ssim_visualization is False
        assert config.show_pixel_diff_visualization is True
        assert config.show_color_distance_visualization is False
        assert config.show_histogram_visualization is True
        assert config.show_dimension_visualization is False

        logger.info("✓ Config custom visualization toggles test passed")

    def test_config_flip_all_valid_colormaps(self, temp_image_dir):
        """Config should accept all valid FLIP colormaps."""
        logger.debug("Testing Config with all valid FLIP colormaps")

        valid_colormaps = ["viridis", "jet", "turbo", "magma"]
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True,
            flip_colormaps=valid_colormaps,
            flip_default_colormap="magma",
        )

        assert config.flip_colormaps == valid_colormaps
        assert config.flip_default_colormap == "magma"
        logger.info("✓ Config all valid FLIP colormaps test passed")
