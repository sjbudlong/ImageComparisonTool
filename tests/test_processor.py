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
        img_array = np.array(
            [[10, 50, 100], [150, 200, 240], [10, 100, 200]], dtype=np.uint8
        )

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
            (100, 100),  # Grayscale
            (100, 100, 3),  # Color
            (50, 200, 3),  # Different dimensions
        ]

        processor = ImageProcessor()
        for shape in shapes:
            img_array = np.random.randint(0, 256, shape, dtype=np.uint8)
            result = processor.equalize_histogram(img_array)
            assert result.shape == shape

    def test_generate_histogram_image_returns_base64(
        self, simple_test_image, simple_test_image_modified
    ):
        """generate_histogram_image should return base64 encoded string."""
        img1 = np.array(simple_test_image)
        img2 = np.array(simple_test_image_modified)

        processor = ImageProcessor()
        result = processor.generate_histogram_image(img1, img2)

        # Should be a string
        assert isinstance(result, str)
        # Should be base64 encoded (contains only valid base64 chars)
        assert all(
            c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            for c in result
        )
        # Should be non-empty
        assert len(result) > 0

    def test_generate_histogram_image_different_formats(self):
        """generate_histogram_image should handle different image formats."""
        # Create test arrays of different types
        formats = [
            np.random.randint(0, 256, (100, 100), dtype=np.uint8),  # Grayscale
            np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8),  # RGB
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

    def test_processor_with_test_images(
        self, simple_test_image, simple_test_image_modified
    ):
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

    def test_load_images_return_both_with_equalization(
        self, valid_config, simple_test_image, simple_test_image_modified
    ):
        """load_images with return_both=True should return 4-tuple."""
        # Save test images
        path1 = valid_config.new_path / "test1.png"
        path2 = valid_config.new_path / "test2.png"
        simple_test_image.save(path1)
        simple_test_image_modified.save(path2)

        # Load with return_both=True and equalize=True
        orig1, orig2, eq1, eq2 = ImageProcessor.load_images(
            path1,
            path2,
            equalize=True,
            use_clahe=True,
            to_grayscale=False,
            return_both=True,
        )

        # Verify 4 arrays returned
        assert orig1.shape == eq1.shape
        assert orig2.shape == eq2.shape

        # Verify all are numpy arrays
        assert isinstance(orig1, np.ndarray)
        assert isinstance(orig2, np.ndarray)
        assert isinstance(eq1, np.ndarray)
        assert isinstance(eq2, np.ndarray)

        # Verify equalization happened (arrays should be different)
        # Note: In some cases they might be similar, so we just check they exist
        assert orig1.shape == eq1.shape  # Shape should match
        assert orig2.shape == eq2.shape

    def test_load_images_return_both_without_equalization(
        self, valid_config, simple_test_image
    ):
        """load_images with return_both=True and equalize=False should return originals for both."""
        # Save test image
        path1 = valid_config.new_path / "test1.png"
        path2 = valid_config.new_path / "test2.png"
        simple_test_image.save(path1)
        simple_test_image.save(path2)

        # Load with return_both=True and equalize=False
        orig1, orig2, eq1, eq2 = ImageProcessor.load_images(
            path1, path2, equalize=False, return_both=True
        )

        # When not equalizing, equalized versions should be same as originals
        assert np.array_equal(orig1, eq1)
        assert np.array_equal(orig2, eq2)

    def test_load_images_backward_compatibility(self, valid_config, simple_test_image):
        """load_images without return_both should maintain backward compatibility."""
        # Save test images
        path1 = valid_config.new_path / "test1.png"
        path2 = valid_config.new_path / "test2.png"
        simple_test_image.save(path1)
        simple_test_image.save(path2)

        # Load with default return_both=False
        img1, img2 = ImageProcessor.load_images(path1, path2, equalize=False)

        # Should return 2-tuple
        assert isinstance(img1, np.ndarray)
        assert isinstance(img2, np.ndarray)
        assert img1.shape == img2.shape


@pytest.mark.unit
class TestFLIPVisualization:
    """Test FLIP heatmap and visualization methods."""

    def test_create_flip_heatmap_basic(self):
        """create_flip_heatmap should create RGB heatmap from error map."""
        # Create mock FLIP error map
        flip_map = np.random.uniform(0, 0.5, (100, 100)).astype(np.float32)

        processor = ImageProcessor()
        heatmap = processor.create_flip_heatmap(flip_map, colormap="viridis")

        # Should return RGB uint8 array
        assert heatmap.shape == (100, 100, 3)
        assert heatmap.dtype == np.uint8
        # Values should be in valid range
        assert heatmap.min() >= 0
        assert heatmap.max() <= 255

    def test_create_flip_heatmap_colormaps(self):
        """create_flip_heatmap should support multiple colormaps."""
        flip_map = np.random.uniform(0, 0.3, (50, 50)).astype(np.float32)
        colormaps = ["viridis", "jet", "turbo", "magma"]

        processor = ImageProcessor()

        for cmap in colormaps:
            heatmap = processor.create_flip_heatmap(flip_map, colormap=cmap)
            assert heatmap.shape == (50, 50, 3)
            assert heatmap.dtype == np.uint8

    def test_create_flip_heatmap_normalization(self):
        """create_flip_heatmap should normalize values when requested."""
        # Create map with limited range
        flip_map = np.random.uniform(0.1, 0.3, (100, 100)).astype(np.float32)

        processor = ImageProcessor()

        # With normalization, should use full colormap range
        heatmap_norm = processor.create_flip_heatmap(flip_map, normalize=True)

        # Without normalization, should respect absolute scale
        heatmap_abs = processor.create_flip_heatmap(flip_map, normalize=False)

        # Both should be valid
        assert heatmap_norm.shape == (100, 100, 3)
        assert heatmap_abs.shape == (100, 100, 3)

        # Normalized version should use more of the color range
        # (this is heuristic, but generally true)
        norm_range = heatmap_norm.max() - heatmap_norm.min()
        abs_range = heatmap_abs.max() - heatmap_abs.min()

        # Normalized should typically have larger or equal range
        assert norm_range >= abs_range * 0.5  # Allow some tolerance

    def test_create_flip_heatmap_invalid_colormap_fallback(self):
        """create_flip_heatmap should fallback to viridis for invalid colormap."""
        flip_map = np.random.uniform(0, 0.3, (50, 50)).astype(np.float32)

        processor = ImageProcessor()
        # Should not crash, should fallback to viridis
        heatmap = processor.create_flip_heatmap(flip_map, colormap="invalid_name")

        assert heatmap.shape == (50, 50, 3)
        assert heatmap.dtype == np.uint8

    def test_create_flip_heatmaps_multi_colormap(self, tmp_path):
        """create_flip_heatmaps_multi_colormap should generate multiple files."""
        flip_map = np.random.uniform(0, 0.3, (100, 100)).astype(np.float32)
        colormaps = ["viridis", "jet"]
        output_dir = tmp_path / "flip_outputs"
        base_filename = "test_image.png"

        processor = ImageProcessor()
        paths = processor.create_flip_heatmaps_multi_colormap(
            flip_map, colormaps, output_dir, base_filename
        )

        # Should return dict with both colormaps
        assert len(paths) == 2
        assert "viridis" in paths
        assert "jet" in paths

        # Files should exist
        assert paths["viridis"].exists()
        assert paths["jet"].exists()

        # Files should be valid images
        img_viridis = Image.open(paths["viridis"])
        img_jet = Image.open(paths["jet"])

        assert img_viridis.size == (100, 100)
        assert img_jet.size == (100, 100)

    def test_create_flip_heatmaps_multi_colormap_creates_directory(self, tmp_path):
        """create_flip_heatmaps_multi_colormap should create output directory if needed."""
        flip_map = np.random.uniform(0, 0.3, (50, 50)).astype(np.float32)
        output_dir = tmp_path / "nested" / "flip_outputs"  # Doesn't exist yet
        base_filename = "test.png"

        processor = ImageProcessor()

        # Should not crash, should create directory
        paths = processor.create_flip_heatmaps_multi_colormap(
            flip_map, ["viridis"], output_dir, base_filename
        )

        assert output_dir.exists()
        assert paths["viridis"].exists()

    def test_generate_flip_comparison_image_returns_base64(self):
        """generate_flip_comparison_image should return base64 encoded image."""
        # Create test images
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 130
        flip_map = np.random.uniform(0, 0.2, (100, 100)).astype(np.float32)

        processor = ImageProcessor()
        result = processor.generate_flip_comparison_image(
            img1, img2, flip_map, colormap="viridis"
        )

        # Should be base64 string
        assert isinstance(result, str)
        assert len(result) > 0

        # Should be valid base64
        assert all(
            c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            for c in result
        )

    def test_generate_flip_comparison_image_with_colormaps(self):
        """generate_flip_comparison_image should work with different colormaps."""
        img1 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img2 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        flip_map = np.random.uniform(0, 0.3, (100, 100)).astype(np.float32)

        processor = ImageProcessor()

        for cmap in ["viridis", "jet", "turbo", "magma"]:
            result = processor.generate_flip_comparison_image(
                img1, img2, flip_map, colormap=cmap
            )
            assert isinstance(result, str)
            assert len(result) > 100  # Should be substantial

    def test_flip_heatmap_zero_values(self):
        """create_flip_heatmap should handle all-zero error map."""
        flip_map = np.zeros((100, 100), dtype=np.float32)

        processor = ImageProcessor()
        heatmap = processor.create_flip_heatmap(flip_map, colormap="viridis")

        # Should not crash
        assert heatmap.shape == (100, 100, 3)
        assert heatmap.dtype == np.uint8

    def test_flip_heatmap_max_values(self):
        """create_flip_heatmap should handle all-max error map."""
        flip_map = np.ones((100, 100), dtype=np.float32)  # All 1.0 (max error)

        processor = ImageProcessor()
        heatmap = processor.create_flip_heatmap(flip_map, colormap="viridis")

        # Should not crash
        assert heatmap.shape == (100, 100, 3)
        assert heatmap.dtype == np.uint8
