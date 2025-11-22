"""
Unit tests for processor module.
"""

import pytest
import numpy as np
from PIL import Image
from processor import ImageProcessor


@pytest.mark.unit
class TestImageProcessor:
    """Test ImageProcessor functionality."""
    
    def test_equalize_histogram_grayscale(self):
        """equalize_histogram should work on grayscale images."""
        # Create a simple grayscale image with low contrast
        img_array = np.array([
            [10, 50, 100],
            [150, 200, 240],
            [10, 100, 200]
        ], dtype=np.uint8)
        
        processor = ImageProcessor()
        result = processor.equalize_histogram(img_array)
        
        assert result.shape == img_array.shape
        assert result.dtype == np.uint8
        # Equalized histogram should be different from original
        # (doesn't always have more spread, but should spread values across range)
        assert not np.array_equal(result, img_array)
    
    def test_equalize_histogram_color(self):
        """equalize_histogram should work on color images."""
        # Create a simple color image
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        img_array[:, :, 0] = 100  # Red channel
        img_array[:, :, 1] = 150  # Green channel
        img_array[:, :, 2] = 200  # Blue channel
        
        processor = ImageProcessor()
        result = processor.equalize_histogram(img_array)
        
        assert result.shape == img_array.shape
        assert result.dtype == np.uint8
        # Should have 3 channels
        assert result.shape[2] == 3
    
    def test_equalize_histogram_preserves_shape(self):
        """equalize_histogram should preserve image shape."""
        shapes = [
            (100, 100),      # Grayscale
            (100, 100, 3),   # Color
            (50, 200, 3),    # Different dimensions
        ]
        
        processor = ImageProcessor()
        for shape in shapes:
            img_array = np.random.randint(0, 256, shape, dtype=np.uint8)
            result = processor.equalize_histogram(img_array)
            assert result.shape == shape
    
    def test_generate_histogram_image_returns_base64(self, simple_test_image, simple_test_image_modified):
        """generate_histogram_image should return base64 encoded string."""
        img1 = np.array(simple_test_image)
        img2 = np.array(simple_test_image_modified)
        
        processor = ImageProcessor()
        result = processor.generate_histogram_image(img1, img2)
        
        # Should be a string
        assert isinstance(result, str)
        # Should be base64 encoded (contains only valid base64 chars)
        assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in result)
        # Should be non-empty
        assert len(result) > 0
    
    def test_generate_histogram_image_different_formats(self):
        """generate_histogram_image should handle different image formats."""
        # Create test arrays of different types
        formats = [
            np.random.randint(0, 256, (100, 100), dtype=np.uint8),      # Grayscale
            np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8),   # RGB
        ]
        
        processor = ImageProcessor()
        for img_array in formats:
            # Create a copy with slight differences
            img_array2 = img_array.copy()
            img_array2[0:10, 0:10] = 0  # Darken small area
            
            result = processor.generate_histogram_image(img_array, img_array2)
            assert isinstance(result, str)
            assert len(result) > 0


@pytest.mark.unit
class TestImageProcessorIntegration:
    """Integration-like tests for ImageProcessor."""
    
    def test_processor_with_test_images(self, simple_test_image, simple_test_image_modified):
        """Test processor with actual PIL images."""
        img1 = np.array(simple_test_image)
        img2 = np.array(simple_test_image_modified)
        
        processor = ImageProcessor()
        
        # Test histogram generation
        hist_data = processor.generate_histogram_image(img1, img2)
        assert isinstance(hist_data, str)
        assert len(hist_data) > 100  # Should be substantial base64 string
    
    def test_processor_with_identical_images(self, simple_test_image):
        """Test processor with identical images."""
        img_array = np.array(simple_test_image)
        
        processor = ImageProcessor()
        hist_data = processor.generate_histogram_image(img_array, img_array)
        
        # Should still produce valid output
        assert isinstance(hist_data, str)
        assert len(hist_data) > 0
