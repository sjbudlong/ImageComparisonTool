"""
Unit tests for image analyzer modules.
"""

import pytest
import logging
import numpy as np
from PIL import Image
from analyzers import (
    PixelDifferenceAnalyzer,
    StructuralSimilarityAnalyzer,
    ColorDifferenceAnalyzer,
    DimensionAnalyzer,
    HistogramAnalyzer,
    AnalyzerRegistry,
)
from config import Config

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestPixelDifferenceAnalyzer:
    """Test PixelDifferenceAnalyzer."""

    def test_analyzer_name(self):
        """Analyzer should have correct name."""
        analyzer = PixelDifferenceAnalyzer()
        assert analyzer.name == "Pixel Difference"

    def test_identical_images(self):
        """Identical images should have 0% difference."""
        logger.debug("Testing PixelDifferenceAnalyzer with identical images")

        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        analyzer = PixelDifferenceAnalyzer(threshold=1)

        result = analyzer.analyze(img, img)

        assert result["percent_different"] == 0.0
        assert result["changed_pixels"] == 0
        assert result["mean_absolute_error"] == 0.0
        assert result["max_difference"] == 0.0

        logger.info("✓ PixelDifferenceAnalyzer identical images test passed")

    def test_completely_different_images(self):
        """Completely different images should have high difference."""
        logger.debug("Testing PixelDifferenceAnalyzer with completely different images")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        analyzer = PixelDifferenceAnalyzer(threshold=1)
        result = analyzer.analyze(img1, img2)

        assert result["percent_different"] == 100.0
        assert result["changed_pixels"] == img1.size
        assert result["max_difference"] == 255.0

        logger.info("✓ PixelDifferenceAnalyzer completely different images test passed")

    def test_threshold_application(self):
        """Threshold should correctly filter small differences."""
        logger.debug("Testing PixelDifferenceAnalyzer threshold application")

        # Create images with small difference (within threshold)
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 100
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 101  # Difference of 1

        # With threshold=1, should not count as different
        analyzer_strict = PixelDifferenceAnalyzer(threshold=1)
        result_strict = analyzer_strict.analyze(img1, img2)

        # With threshold=0, should count as different
        analyzer_loose = PixelDifferenceAnalyzer(threshold=0)
        result_loose = analyzer_loose.analyze(img1, img2)

        assert result_strict["percent_different"] == 0.0
        assert result_loose["percent_different"] == 100.0

        logger.info("✓ PixelDifferenceAnalyzer threshold application test passed")

    def test_mean_absolute_error(self):
        """MAE should be calculated correctly."""
        logger.debug("Testing PixelDifferenceAnalyzer MAE calculation")

        img1 = np.zeros((100, 100), dtype=np.uint8)
        img2 = np.ones((100, 100), dtype=np.uint8) * 10

        analyzer = PixelDifferenceAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["mean_absolute_error"] == 10.0

        logger.info("✓ PixelDifferenceAnalyzer MAE test passed")


@pytest.mark.unit
class TestStructuralSimilarityAnalyzer:
    """Test StructuralSimilarityAnalyzer."""

    def test_analyzer_name(self):
        """Analyzer should have correct name."""
        analyzer = StructuralSimilarityAnalyzer()
        assert analyzer.name == "Structural Similarity"

    def test_identical_images_ssim(self):
        """Identical images should have SSIM score of 1.0."""
        logger.debug("Testing SSIM with identical images")

        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        analyzer = StructuralSimilarityAnalyzer()

        result = analyzer.analyze(img, img)

        assert result["ssim_score"] == 1.0
        assert result["ssim_percentage"] == 0.0
        assert result["ssim_description"] == "Nearly identical"

        logger.info("✓ SSIM identical images test passed")

    def test_different_images_ssim(self):
        """Different images should have SSIM score less than 1.0."""
        logger.debug("Testing SSIM with different images")

        img1 = np.zeros((100, 100), dtype=np.uint8)
        img2 = np.ones((100, 100), dtype=np.uint8) * 255

        analyzer = StructuralSimilarityAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["ssim_score"] < 1.0
        assert result["ssim_percentage"] > 0.0

        logger.info("✓ SSIM different images test passed")

    def test_color_image_conversion(self):
        """SSIM should convert color images to grayscale."""
        logger.debug("Testing SSIM with color images")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)

        analyzer = StructuralSimilarityAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["ssim_score"] == 1.0

        logger.info("✓ SSIM color image conversion test passed")

    def test_ssim_description_ranges(self):
        """SSIM descriptions should match score ranges."""
        logger.debug("Testing SSIM description ranges")

        analyzer = StructuralSimilarityAnalyzer()

        assert analyzer._describe_ssim(1.0) == "Nearly identical"
        assert analyzer._describe_ssim(0.99) == "Nearly identical"
        assert analyzer._describe_ssim(0.97) == "Very similar"
        assert analyzer._describe_ssim(0.92) == "Similar"
        assert analyzer._describe_ssim(0.85) == "Somewhat similar"
        assert analyzer._describe_ssim(0.75) == "Moderately different"
        assert analyzer._describe_ssim(0.60) == "Very different"

        logger.info("✓ SSIM description ranges test passed")


@pytest.mark.unit
class TestColorDifferenceAnalyzer:
    """Test ColorDifferenceAnalyzer."""

    def test_analyzer_name(self):
        """Analyzer should have correct name."""
        analyzer = ColorDifferenceAnalyzer()
        assert analyzer.name == "Color Difference"

    def test_grayscale_image_detection(self):
        """Analyzer should detect grayscale images."""
        logger.debug("Testing ColorDifferenceAnalyzer grayscale detection")

        img1 = np.zeros((100, 100), dtype=np.uint8)
        img2 = np.zeros((100, 100), dtype=np.uint8)

        analyzer = ColorDifferenceAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["grayscale"] is True
        assert "message" in result

        logger.info("✓ ColorDifferenceAnalyzer grayscale detection test passed")

    def test_color_channel_differences(self):
        """Analyzer should calculate per-channel differences."""
        logger.debug("Testing ColorDifferenceAnalyzer channel differences")

        # Create images with different color channels
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[:, :, 0] = 50  # Red channel different

        analyzer = ColorDifferenceAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["grayscale"] is False
        assert result["red_mean_diff"] == 50.0
        assert result["green_mean_diff"] == 0.0
        assert result["blue_mean_diff"] == 0.0
        assert result["red_max_diff"] == 50.0

        logger.info("✓ ColorDifferenceAnalyzer channel differences test passed")

    def test_color_distance_calculation(self):
        """Analyzer should calculate Euclidean color distance."""
        logger.debug("Testing ColorDifferenceAnalyzer color distance")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[:, :, 0] = 3  # R
        img2[:, :, 1] = 4  # G
        # Expected distance: sqrt(3^2 + 4^2) = 5

        analyzer = ColorDifferenceAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["mean_color_distance"] == 5.0
        assert result["max_color_distance"] == 5.0

        logger.info("✓ ColorDifferenceAnalyzer color distance test passed")

    def test_significant_color_changes_threshold(self):
        """Analyzer should count pixels exceeding threshold."""
        logger.debug("Testing ColorDifferenceAnalyzer threshold")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        # Make 25% of pixels have large change
        img2[:50, :50, :] = 100

        analyzer = ColorDifferenceAnalyzer(distance_threshold=10.0)
        result = analyzer.analyze(img1, img2)

        assert result["significant_change_percent"] == 25.0
        assert result["significant_color_changes"] == 2500  # 50*50
        assert result["threshold_used"] == 10.0

        logger.info("✓ ColorDifferenceAnalyzer threshold test passed")


@pytest.mark.unit
class TestDimensionAnalyzer:
    """Test DimensionAnalyzer."""

    def test_analyzer_name(self):
        """Analyzer should have correct name."""
        analyzer = DimensionAnalyzer()
        assert analyzer.name == "Dimensions"

    def test_matching_dimensions(self):
        """Analyzer should detect matching dimensions."""
        logger.debug("Testing DimensionAnalyzer with matching dimensions")

        img1 = np.zeros((100, 200, 3), dtype=np.uint8)
        img2 = np.zeros((100, 200, 3), dtype=np.uint8)

        analyzer = DimensionAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["shapes_match"] is True
        assert result["img1_size"] == "200x100"
        assert result["img2_size"] == "200x100"

        logger.info("✓ DimensionAnalyzer matching dimensions test passed")

    def test_mismatched_dimensions(self):
        """Analyzer should detect mismatched dimensions."""
        logger.debug("Testing DimensionAnalyzer with mismatched dimensions")

        img1 = np.zeros((100, 200, 3), dtype=np.uint8)
        img2 = np.zeros((150, 250, 3), dtype=np.uint8)

        analyzer = DimensionAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["shapes_match"] is False
        assert result["img1_size"] == "200x100"
        assert result["img2_size"] == "250x150"

        logger.info("✓ DimensionAnalyzer mismatched dimensions test passed")


@pytest.mark.unit
class TestHistogramAnalyzer:
    """Test HistogramAnalyzer."""

    def test_analyzer_name(self):
        """Analyzer should have correct name."""
        analyzer = HistogramAnalyzer()
        assert analyzer.name == "Histogram Analysis"

    def test_identical_color_images(self):
        """Identical color images should have perfect correlation."""
        logger.debug("Testing HistogramAnalyzer with identical color images")

        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        analyzer = HistogramAnalyzer()
        result = analyzer.analyze(img, img)

        assert result["red_histogram_correlation"] == 1.0
        assert result["green_histogram_correlation"] == 1.0
        assert result["blue_histogram_correlation"] == 1.0
        assert result["red_histogram_chi_square"] == 0.0
        assert result["green_histogram_chi_square"] == 0.0
        assert result["blue_histogram_chi_square"] == 0.0

        logger.info("✓ HistogramAnalyzer identical color images test passed")

    def test_identical_grayscale_images(self):
        """Identical grayscale images should have perfect correlation."""
        logger.debug("Testing HistogramAnalyzer with identical grayscale images")

        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

        analyzer = HistogramAnalyzer()
        result = analyzer.analyze(img, img)

        assert result["histogram_correlation"] == 1.0
        assert result["histogram_chi_square"] == 0.0

        logger.info("✓ HistogramAnalyzer identical grayscale images test passed")

    def test_different_color_images(self):
        """Different color images should have lower correlation."""
        logger.debug("Testing HistogramAnalyzer with different color images")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        analyzer = HistogramAnalyzer()
        result = analyzer.analyze(img1, img2)

        # Should have some correlation metrics
        assert "red_histogram_correlation" in result
        assert "green_histogram_correlation" in result
        assert "blue_histogram_correlation" in result
        assert "red_histogram_chi_square" in result

        logger.info("✓ HistogramAnalyzer different color images test passed")

    def test_grayscale_vs_color_output(self):
        """Grayscale and color images should have different output structures."""
        logger.debug("Testing HistogramAnalyzer output structure")

        gray_img = np.zeros((100, 100), dtype=np.uint8)
        color_img = np.zeros((100, 100, 3), dtype=np.uint8)

        analyzer = HistogramAnalyzer()

        gray_result = analyzer.analyze(gray_img, gray_img)
        color_result = analyzer.analyze(color_img, color_img)

        # Grayscale should have simple keys
        assert "histogram_correlation" in gray_result
        assert "red_histogram_correlation" not in gray_result

        # Color should have channel-specific keys
        assert "red_histogram_correlation" in color_result
        assert "histogram_correlation" not in color_result

        logger.info("✓ HistogramAnalyzer output structure test passed")


@pytest.mark.unit
class TestAnalyzerRegistry:
    """Test AnalyzerRegistry."""

    def test_registry_initialization(self):
        """Registry should initialize with default analyzers."""
        logger.debug("Testing AnalyzerRegistry initialization")

        registry = AnalyzerRegistry()

        assert len(registry.analyzers) == 5  # Default analyzers
        analyzer_names = [a.name for a in registry.analyzers]
        assert "Dimensions" in analyzer_names
        assert "Histogram Analysis" in analyzer_names
        assert "Pixel Difference" in analyzer_names
        assert "Color Difference" in analyzer_names
        assert "Structural Similarity" in analyzer_names

        logger.info("✓ AnalyzerRegistry initialization test passed")

    def test_registry_with_config(self, base_config):
        """Registry should use config thresholds when provided."""
        logger.debug("Testing AnalyzerRegistry with config")

        registry = AnalyzerRegistry(base_config)

        # Find PixelDifferenceAnalyzer
        pixel_analyzer = None
        for analyzer in registry.analyzers:
            if isinstance(analyzer, PixelDifferenceAnalyzer):
                pixel_analyzer = analyzer
                break

        assert pixel_analyzer is not None
        assert pixel_analyzer.threshold == base_config.pixel_change_threshold

        logger.info("✓ AnalyzerRegistry with config test passed")

    def test_register_custom_analyzer(self):
        """Registry should allow registering custom analyzers."""
        logger.debug("Testing custom analyzer registration")

        registry = AnalyzerRegistry()
        initial_count = len(registry.analyzers)

        # Register another analyzer
        custom_analyzer = DimensionAnalyzer()
        registry.register(custom_analyzer)

        assert len(registry.analyzers) == initial_count + 1

        logger.info("✓ Custom analyzer registration test passed")

    def test_analyze_all(self):
        """analyze_all should run all registered analyzers."""
        logger.debug("Testing analyze_all")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 100

        registry = AnalyzerRegistry()
        results = registry.analyze_all(img1, img2)

        # Should have results from all default analyzers
        assert "Dimensions" in results
        assert "Histogram Analysis" in results
        assert "Pixel Difference" in results
        assert "Color Difference" in results
        assert "Structural Similarity" in results

        # Each result should be a dictionary
        assert isinstance(results["Dimensions"], dict)
        assert isinstance(results["Pixel Difference"], dict)

        logger.info("✓ analyze_all test passed")

    def test_analyze_all_error_handling(self):
        """analyze_all should handle analyzer errors gracefully."""
        logger.debug("Testing analyze_all error handling")

        # Create a custom analyzer that raises an error
        class ErrorAnalyzer(DimensionAnalyzer):
            @property
            def name(self):
                return "Error Analyzer"

            def analyze(self, img1, img2):
                raise ValueError("Test error")

        registry = AnalyzerRegistry()
        registry.register(ErrorAnalyzer())

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)

        results = registry.analyze_all(img1, img2)

        # Error analyzer should have an error in results
        assert "Error Analyzer" in results
        assert "error" in results["Error Analyzer"]

        logger.info("✓ analyze_all error handling test passed")

    def test_analyzer_results_structure(self):
        """Analyzer results should have expected structure."""
        logger.debug("Testing analyzer results structure")

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[:, :, 0] = 50

        registry = AnalyzerRegistry()
        results = registry.analyze_all(img1, img2)

        # Verify Pixel Difference result structure
        pixel_result = results["Pixel Difference"]
        assert "percent_different" in pixel_result
        assert "changed_pixels" in pixel_result
        assert "total_pixels" in pixel_result
        assert "mean_absolute_error" in pixel_result

        # Verify SSIM result structure
        ssim_result = results["Structural Similarity"]
        assert "ssim_score" in ssim_result
        assert "ssim_percentage" in ssim_result
        assert "ssim_description" in ssim_result

        # Verify Dimensions result structure
        dim_result = results["Dimensions"]
        assert "shapes_match" in dim_result
        assert "img1_size" in dim_result
        assert "img2_size" in dim_result

        logger.info("✓ Analyzer results structure test passed")
