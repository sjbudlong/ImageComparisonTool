"""
Pytest configuration and shared fixtures.
"""

import sys
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

# Add ImageComparisonSystem to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ImageComparisonSystem"))

from config import Config
from logging_config import setup_logging

# Configure logging for tests
setup_logging(level=0)  # NOTSET - capture all levels


@pytest.fixture
def temp_image_dir(tmp_path):
    """Create temporary directory with test images."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    return images_dir


@pytest.fixture
def simple_test_image():
    """Create a simple test image."""
    # Create a 100x100 red image
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    img_array[:, :, 0] = 255  # Red channel
    img = Image.fromarray(img_array, 'RGB')
    return img


@pytest.fixture
def simple_test_image_modified():
    """Create a slightly modified test image (for diff testing)."""
    # Create a 100x100 image with some differences
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    img_array[:, :, 0] = 255  # Red channel
    img_array[10:20, 10:20, :] = [0, 255, 0]  # Green square
    img = Image.fromarray(img_array, 'RGB')
    return img


@pytest.fixture
def new_and_known_good_dirs(temp_image_dir, simple_test_image, simple_test_image_modified):
    """Create new and known_good directories with test images."""
    new_dir = temp_image_dir / "new"
    known_good_dir = temp_image_dir / "known_good"
    new_dir.mkdir()
    known_good_dir.mkdir()
    
    # Save test images
    simple_test_image.save(new_dir / "test1.png")
    simple_test_image_modified.save(known_good_dir / "test1.png")
    
    simple_test_image.save(new_dir / "test2.jpg")
    simple_test_image.save(known_good_dir / "test2.jpg")
    
    return new_dir, known_good_dir


@pytest.fixture
def base_config(temp_image_dir):
    """Create a basic Config object for testing."""
    return Config(
        base_dir=temp_image_dir,
        new_dir="new",
        known_good_dir="known_good",
        pixel_diff_threshold=0.01,
        ssim_threshold=0.95
    )


@pytest.fixture
def valid_config(temp_image_dir, new_and_known_good_dirs):
    """Create a valid Config with actual directories."""
    new_dir, known_good_dir = new_and_known_good_dirs
    config = Config(
        base_dir=temp_image_dir,
        new_dir="new",
        known_good_dir="known_good",
        pixel_diff_threshold=0.01,
        ssim_threshold=0.95
    )
    return config


# Pytest markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
