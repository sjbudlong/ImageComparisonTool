"""
Unit tests for config module.
"""

import pytest
import logging
from pathlib import Path
from config import Config


# Get logger for this module
logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestConfig:
    """Test Config dataclass."""
    
    def test_config_creation_with_path_object(self, temp_image_dir):
        """Config should accept Path objects."""
        logger.debug(f"Testing config creation with Path object: {temp_image_dir}")
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        assert isinstance(config.base_dir, Path)
        assert config.new_dir == "new"
        assert config.known_good_dir == "known_good"
        logger.info("✓ Config creation with Path object test passed")
    
    def test_config_creation_with_string_path(self, temp_image_dir):
        """Config should convert string paths to Path objects."""
        logger.debug(f"Testing config creation with string path: {str(temp_image_dir)}")
        config = Config(
            base_dir=str(temp_image_dir),
            new_dir="new",
            known_good_dir="known_good"
        )
        assert isinstance(config.base_dir, Path)
        logger.info("✓ Config creation with string path test passed")
    
    def test_config_default_values(self, temp_image_dir):
        """Config should have sensible default values."""
        logger.debug("Testing config default values")
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
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
            highlight_color=(0, 255, 0)
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
            html_dir="reports"
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
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
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
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
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
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
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
        config = Config(
            base_dir=new_base,
            new_dir="new",
            known_good_dir="known_good"
        )
        assert config.base_dir.exists()
        logger.info("✓ Config base_dir creation test passed")
