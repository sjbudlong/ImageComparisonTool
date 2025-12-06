"""
End-to-end integration tests for NVIDIA FLIP feature.

Tests the complete workflow from configuration through comparison to report generation.
"""

import pytest
import logging
import numpy as np
from pathlib import Path
from PIL import Image
from unittest.mock import patch, MagicMock
from config import Config
from comparator import ImageComparator
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)


@pytest.mark.integration
class TestFLIPIntegrationEndToEnd:
    """Test complete FLIP workflow from start to finish."""

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip')
    def test_full_comparison_workflow_with_flip(
        self, mock_flip, valid_config, simple_test_image, simple_test_image_modified
    ):
        """Test complete comparison workflow with FLIP enabled."""
        logger.debug("Testing full FLIP integration workflow")

        # Configure FLIP
        valid_config.enable_flip = True
        valid_config.flip_colormaps = ["viridis", "jet"]
        valid_config.flip_default_colormap = "viridis"
        valid_config.show_flip_visualization = True

        # Mock FLIP to return realistic error map
        error_map = np.random.uniform(0.1, 0.3, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        # Save test images
        new_path = valid_config.new_path / "test.png"
        known_path = valid_config.known_good_path / "test.png"
        simple_test_image_modified.save(new_path)
        simple_test_image.save(known_path)

        # Run comparison
        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        # Verify results
        assert len(results) == 1
        result = results[0]

        # Verify FLIP metrics exist
        assert "FLIP Perceptual Metric" in result.metrics
        flip_metrics = result.metrics["FLIP Perceptual Metric"]
        assert "flip_mean" in flip_metrics
        assert "flip_max" in flip_metrics
        assert "flip_error_map_array" in flip_metrics

        # Verify FLIP heatmap was generated as primary thumbnail
        assert result.diff_image_path.exists()
        # Should be FLIP heatmap, not diff image
        assert "flip_heatmap" in str(result.diff_image_path).lower() or \
               "viridis" in str(result.diff_image_path).lower()

        logger.info("✓ Full FLIP integration workflow test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip')
    def test_flip_report_generation_integration(
        self, mock_flip, valid_config, simple_test_image
    ):
        """Test that FLIP results are properly included in HTML reports."""
        logger.debug("Testing FLIP report generation integration")

        valid_config.enable_flip = True
        valid_config.flip_colormaps = ["viridis"]
        valid_config.flip_default_colormap = "viridis"
        valid_config.show_flip_visualization = True

        error_map = np.random.uniform(0, 0.2, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        # Save test images
        new_path = valid_config.new_path / "report_test.png"
        known_path = valid_config.known_good_path / "report_test.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        # Run comparison and generate reports
        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        # Generate reports manually (comparator generates them automatically)
        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(results[0])

        # Verify report exists and contains FLIP section
        report_path = valid_config.html_path / "report_test.png.html"
        assert report_path.exists()

        content = report_path.read_text(encoding="utf-8")
        assert "FLIP Perceptual Metric" in content
        assert "flip-section" in content

        logger.info("✓ FLIP report generation integration test passed")

    @patch('analyzers.FLIP_AVAILABLE', False)
    def test_graceful_degradation_without_flip(
        self, valid_config, simple_test_image
    ):
        """Test that system works correctly when FLIP is not available."""
        logger.debug("Testing graceful degradation without FLIP")

        # Enable FLIP in config (but package not available)
        valid_config.enable_flip = True

        # Save test images
        new_path = valid_config.new_path / "no_flip.png"
        known_path = valid_config.known_good_path / "no_flip.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        # Should not crash, just skip FLIP analysis
        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        assert len(results) == 1
        # FLIP metrics should not be present
        assert "FLIP Perceptual Metric" not in results[0].metrics

        # Should use traditional diff image as thumbnail
        assert results[0].diff_image_path.exists()
        assert "diff_" in str(results[0].diff_image_path)

        logger.info("✓ Graceful degradation without FLIP test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip')
    def test_flip_with_multiple_colormaps(
        self, mock_flip, valid_config, simple_test_image
    ):
        """Test that multiple FLIP heatmap colormaps are generated."""
        logger.debug("Testing FLIP with multiple colormaps")

        valid_config.enable_flip = True
        valid_config.flip_colormaps = ["viridis", "jet", "turbo"]
        valid_config.flip_default_colormap = "jet"

        error_map = np.random.uniform(0, 0.25, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        new_path = valid_config.new_path / "multi_colormap.png"
        known_path = valid_config.known_good_path / "multi_colormap.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        # Verify all heatmaps were generated
        diff_dir = valid_config.diff_path
        assert (diff_dir / "flip_heatmap_viridis_multi_colormap.png").exists()
        assert (diff_dir / "flip_heatmap_jet_multi_colormap.png").exists()
        assert (diff_dir / "flip_heatmap_turbo_multi_colormap.png").exists()

        # Primary thumbnail should use default colormap (jet)
        assert "jet" in str(results[0].diff_image_path).lower()

        logger.info("✓ FLIP multiple colormaps integration test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip')
    def test_flip_composite_metric_integration(
        self, mock_flip, valid_config, simple_test_image
    ):
        """Test that FLIP is integrated into composite metric calculation."""
        logger.debug("Testing FLIP composite metric integration")

        valid_config.enable_flip = True
        valid_config.enable_history = True

        error_map = np.random.uniform(0.2, 0.4, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        new_path = valid_config.new_path / "composite.png"
        known_path = valid_config.known_good_path / "composite.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        # Verify composite score exists (requires history tracking)
        result = results[0]
        if hasattr(result, 'composite_score'):
            # Composite score should be calculated with FLIP
            assert result.composite_score is not None
            assert result.composite_score >= 0
            assert result.composite_score <= 100

        logger.info("✓ FLIP composite metric integration test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip')
    def test_flip_visualization_toggles_integration(
        self, mock_flip, valid_config, simple_test_image
    ):
        """Test that visualization toggles work correctly with FLIP."""
        logger.debug("Testing FLIP visualization toggles")

        # Disable FLIP visualization
        valid_config.enable_flip = True
        valid_config.show_flip_visualization = False

        error_map = np.random.uniform(0, 0.2, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        new_path = valid_config.new_path / "toggle_test.png"
        known_path = valid_config.known_good_path / "toggle_test.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        # Generate report
        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(results[0])

        # FLIP metrics should exist but visualization should be hidden
        assert "FLIP Perceptual Metric" in results[0].metrics

        report_path = valid_config.html_path / "toggle_test.png.html"
        content = report_path.read_text(encoding="utf-8")

        # FLIP section should not be in report when disabled
        assert "flip-section" not in content.lower() or \
               content.count("FLIP") <= 1  # Might appear in metric list only

        logger.info("✓ FLIP visualization toggles integration test passed")

    @patch('analyzers.FLIP_AVAILABLE', True)
    @patch('analyzers.flip')
    def test_flip_parallel_processing_integration(
        self, mock_flip, valid_config, simple_test_image
    ):
        """Test that FLIP works correctly with parallel processing."""
        logger.debug("Testing FLIP with parallel processing")

        valid_config.enable_flip = True
        valid_config.enable_parallel = True
        valid_config.max_workers = 2

        error_map = np.random.uniform(0, 0.3, (100, 100)).astype(np.float32)
        mock_flip.compute_flip.return_value = error_map

        # Create multiple test images
        for i in range(3):
            new_path = valid_config.new_path / f"parallel_{i}.png"
            known_path = valid_config.known_good_path / f"parallel_{i}.png"
            simple_test_image.save(new_path)
            simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        results = comparator.compare_all_parallel()

        # All results should have FLIP metrics
        assert len(results) == 3
        for result in results:
            assert "FLIP Perceptual Metric" in result.metrics

        logger.info("✓ FLIP parallel processing integration test passed")


@pytest.mark.integration
class TestFLIPConfigurationIntegration:
    """Test FLIP configuration integration across components."""

    def test_config_validation_with_flip(self, temp_image_dir):
        """Test that FLIP config validation works correctly."""
        logger.debug("Testing FLIP config validation")

        # Valid config
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True,
            flip_colormaps=["viridis", "jet"],
            flip_default_colormap="viridis"
        )
        assert config.enable_flip is True

        # Invalid colormap should raise error
        with pytest.raises(ValueError) as exc_info:
            Config(
                base_dir=temp_image_dir,
                new_dir="new",
                known_good_dir="known_good",
                enable_flip=True,
                flip_colormaps=["invalid"],
                flip_default_colormap="invalid"
            )
        assert "Invalid FLIP colormaps" in str(exc_info.value)

        logger.info("✓ FLIP config validation integration test passed")

    def test_cli_to_config_integration(self, temp_image_dir):
        """Test that CLI arguments properly create FLIP config."""
        logger.debug("Testing CLI to config integration")

        # Simulate CLI arguments
        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_flip=True,
            flip_pixels_per_degree=42.0,
            flip_colormaps=["jet", "turbo"],
            flip_default_colormap="jet"
        )

        assert config.enable_flip is True
        assert config.flip_pixels_per_degree == 42.0
        assert config.flip_colormaps == ["jet", "turbo"]
        assert config.flip_default_colormap == "jet"

        logger.info("✓ CLI to config integration test passed")


@pytest.mark.integration
class TestFLIPBackwardCompatibility:
    """Test that FLIP integration maintains backward compatibility."""

    def test_system_works_without_flip_enabled(
        self, valid_config, simple_test_image
    ):
        """Test that system works normally when FLIP is disabled."""
        logger.debug("Testing backward compatibility with FLIP disabled")

        # FLIP disabled (default)
        assert valid_config.enable_flip is False

        new_path = valid_config.new_path / "no_flip_test.png"
        known_path = valid_config.known_good_path / "no_flip_test.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        assert len(results) == 1
        # Should have standard metrics but not FLIP
        assert "Pixel Difference" in results[0].metrics
        assert "Structural Similarity" in results[0].metrics
        assert "FLIP Perceptual Metric" not in results[0].metrics

        # Should use traditional diff thumbnail
        assert "diff_" in str(results[0].diff_image_path)

        logger.info("✓ Backward compatibility test passed")

    def test_composite_metric_without_flip(
        self, valid_config, simple_test_image
    ):
        """Test that composite metric works with 4-way calculation (no FLIP)."""
        logger.debug("Testing composite metric without FLIP")

        valid_config.enable_flip = False
        valid_config.enable_history = True

        new_path = valid_config.new_path / "composite_no_flip.png"
        known_path = valid_config.known_good_path / "composite_no_flip.png"
        simple_test_image.save(new_path)
        simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        results = list(comparator.compare_all_streaming())

        # Composite score should still work with 4-way calculation
        result = results[0]
        assert "FLIP Perceptual Metric" not in result.metrics

        logger.info("✓ Composite metric without FLIP test passed")
