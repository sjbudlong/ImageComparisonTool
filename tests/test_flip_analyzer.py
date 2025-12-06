"""
Unit tests for FLIP (NVIDIA perceptual metric) analyzer.

Tests cover both scenarios:
1. FLIP package installed (mocked for CI/CD)
2. FLIP package not installed (graceful degradation)
"""

import pytest
import logging
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestFLIPAnalyzer:
    """Test FLIPAnalyzer with mocked FLIP package."""

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_analyzer_name(self, mock_flip_evaluate):
        """Analyzer should have correct name."""
        from analyzers import FLIPAnalyzer

        analyzer = FLIPAnalyzer()
        assert analyzer.name == "FLIP Perceptual Metric"
        logger.info("✓ FLIPAnalyzer name test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_flip_analyzer_initialization(self, mock_flip_evaluate):
        """FLIPAnalyzer should initialize with pixels_per_degree parameter."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer initialization")

        analyzer = FLIPAnalyzer(pixels_per_degree=42.0)
        assert analyzer.pixels_per_degree == 42.0

        # Default value
        analyzer_default = FLIPAnalyzer()
        assert analyzer_default.pixels_per_degree == 67.0

        logger.info("✓ FLIPAnalyzer initialization test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_flip_identical_images(self, mock_flip_evaluate):
        """Identical images should have FLIP error near 0."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer with identical images")

        # Mock flip_evaluate to return (error_map, mean_error, parameters)
        img_shape = (100, 100)
        error_map = np.zeros(img_shape, dtype=np.float32)
        mock_flip_evaluate.return_value = (error_map, 0.0, {"ppd": 67.0})

        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        analyzer = FLIPAnalyzer()

        result = analyzer.analyze(img, img)

        assert result["flip_mean"] == 0.0
        assert result["flip_max"] == 0.0
        assert result["flip_percentile_95"] == 0.0
        assert result["flip_quality_description"] == "Imperceptible differences"
        assert result["pixels_per_degree"] == 67.0

        # Verify flip_evaluate was called
        mock_flip_evaluate.assert_called_once()

        logger.info("✓ FLIPAnalyzer identical images test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_self(self, mock_flip_evaluate):
        """Different images should have FLIP error > 0."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer with different images")

        # Mock FLIP to return realistic error map
        img_shape = (100, 100)
        error_map = np.random.uniform(0.3, 0.5, img_shape).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        analyzer = FLIPAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert result["flip_mean"] > 0.3
        assert result["flip_max"] >= result["flip_mean"]
        assert result["flip_percentile_95"] > 0
        assert result["flip_quality_description"] in [
            "Noticeable perceptual differences",
            "Significant perceptual differences"
        ]

        logger.info("✓ FLIPAnalyzer different images test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_self(self, mock_flip_evaluate):
        """Grayscale images should be converted to RGB."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer grayscale conversion")

        mock_flip.compute_flip.return_value = np.zeros((100, 100), dtype=np.float32)

        # Grayscale images
        img1 = np.ones((100, 100), dtype=np.uint8) * 128
        img2 = np.ones((100, 100), dtype=np.uint8) * 130

        analyzer = FLIPAnalyzer()
        result = analyzer.analyze(img1, img2)

        # Check that compute_flip was called
        mock_flip.compute_flip.assert_called_once()

        # Get the arguments passed to compute_flip
        call_args = mock_flip.compute_flip.call_args
        reference = call_args[1]['reference']  # keyword arg
        test = call_args[1]['test']  # keyword arg

        # Should be 3-channel
        assert reference.shape == (100, 100, 3)
        assert test.shape == (100, 100, 3)

        logger.info("✓ FLIPAnalyzer grayscale conversion test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_self(self, mock_flip_evaluate):
        """FLIP quality descriptions should match thresholds."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer quality descriptions")

        analyzer = FLIPAnalyzer()

        # Test description thresholds
        assert analyzer._describe_flip(0.005) == "Imperceptible differences"
        assert analyzer._describe_flip(0.03) == "Just noticeable differences"
        assert analyzer._describe_flip(0.08) == "Slight perceptual differences"
        assert analyzer._describe_flip(0.15) == "Moderate perceptual differences"
        assert analyzer._describe_flip(0.30) == "Noticeable perceptual differences"
        assert analyzer._describe_flip(0.60) == "Significant perceptual differences"

        logger.info("✓ FLIPAnalyzer quality descriptions test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_self(self, mock_flip_evaluate):
        """Weighted median should only consider non-zero errors."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer weighted median")

        # Create error map with many zeros and some non-zero values
        error_map = np.zeros((100, 100), dtype=np.float32)
        error_map[40:60, 40:60] = 0.5  # Small region with error
        mock_flip.compute_flip.return_value = error_map

        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 130

        analyzer = FLIPAnalyzer()
        result = analyzer.analyze(img1, img2)

        # Weighted median should be close to 0.5 (ignoring zeros)
        assert result["flip_weighted_median"] == 0.5

        # But mean should be much lower (includes all zeros)
        assert result["flip_mean"] < 0.1

        logger.info("✓ FLIPAnalyzer weighted median test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_self(self, mock_flip_evaluate):
        """Result should include full error map for visualization."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer error map inclusion")

        error_map = np.random.uniform(0, 0.3, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 130

        analyzer = FLIPAnalyzer()
        result = analyzer.analyze(img1, img2)

        assert "flip_error_map_array" in result
        assert isinstance(result["flip_error_map_array"], np.ndarray)
        assert result["flip_error_map_array"].shape == (100, 100)

        logger.info("✓ FLIPAnalyzer error map inclusion test passed")

    @patch('analyzers.FLIP_AVAILABLE', False)
    def test_flip_not_available_raises_import_error(self):
        """FLIPAnalyzer should raise ImportError when FLIP not available."""
        from analyzers import FLIPAnalyzer

        logger.debug("Testing FLIPAnalyzer without FLIP package")

        with pytest.raises(ImportError) as exc_info:
            FLIPAnalyzer()

        assert "NVIDIA FLIP not installed" in str(exc_info.value)
        assert "pip install flip-evaluator" in str(exc_info.value)

        logger.info("✓ FLIPAnalyzer ImportError test passed")


@pytest.mark.unit
class TestAnalyzerRegistryWithFLIP:
    """Test AnalyzerRegistry with FLIP integration."""

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_registry_registers_flip_when_enabled(self, mock_flip, temp_image_dir):
        """Registry should register FLIP when available and enabled in config."""
        from analyzers import AnalyzerRegistry
        from config import Config

        logger.debug("Testing AnalyzerRegistry with FLIP enabled")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True,
            flip_pixels_per_degree=42.0
        )

        registry = AnalyzerRegistry(config)

        # Check that FLIP analyzer is registered
        analyzer_names = [a.name for a in registry.analyzers]
        assert "FLIP Perceptual Metric" in analyzer_names

        # Verify correct configuration
        flip_analyzer = next(a for a in registry.analyzers if a.name == "FLIP Perceptual Metric")
        assert flip_analyzer.pixels_per_degree == 42.0

        logger.info("✓ AnalyzerRegistry FLIP registration test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_registry_skips_flip_when_disabled(self, mock_flip, temp_image_dir):
        """Registry should NOT register FLIP when disabled in config."""
        from analyzers import AnalyzerRegistry
        from config import Config

        logger.debug("Testing AnalyzerRegistry with FLIP disabled")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=False  # Explicitly disabled
        )

        registry = AnalyzerRegistry(config)

        # Check that FLIP analyzer is NOT registered
        analyzer_names = [a.name for a in registry.analyzers]
        assert "FLIP Perceptual Metric" not in analyzer_names

        logger.info("✓ AnalyzerRegistry FLIP skip test passed")

    @patch('analyzers.FLIP_AVAILABLE', False)
    def test_registry_skips_flip_when_not_available(self, temp_image_dir):
        """Registry should skip FLIP when package not available."""
        from analyzers import AnalyzerRegistry
        from config import Config

        logger.debug("Testing AnalyzerRegistry with FLIP unavailable")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True  # Enabled but not available
        )

        registry = AnalyzerRegistry(config)

        # Should NOT crash, just skip FLIP
        analyzer_names = [a.name for a in registry.analyzers]
        assert "FLIP Perceptual Metric" not in analyzer_names

        # Other analyzers should still be registered
        assert "Pixel Difference" in analyzer_names
        assert "Structural Similarity" in analyzer_names

        logger.info("✓ AnalyzerRegistry FLIP unavailable test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip_evaluate')
    def test_registry_analyze_all_includes_flip(self, mock_flip, temp_image_dir):
        """Registry.analyze_all should include FLIP results when enabled."""
        from analyzers import AnalyzerRegistry
        from config import Config

        logger.debug("Testing AnalyzerRegistry analyze_all with FLIP")

        # Mock FLIP compute_flip
        mock_flip.compute_flip.return_value = np.zeros((100, 100), dtype=np.float32)

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True
        )

        registry = AnalyzerRegistry(config)

        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 130

        results = registry.analyze_all(img1, img2)

        # Should include FLIP results
        assert "FLIP Perceptual Metric" in results
        assert "flip_mean" in results["FLIP Perceptual Metric"]
        assert "flip_max" in results["FLIP Perceptual Metric"]
        assert "flip_error_map_array" in results["FLIP Perceptual Metric"]

        logger.info("✓ AnalyzerRegistry analyze_all with FLIP test passed")
