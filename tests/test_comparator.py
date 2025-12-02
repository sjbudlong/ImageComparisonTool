"""
Unit tests for ImageComparator class.
"""

import pytest
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from comparator import ImageComparator
from config import Config
from models import ComparisonResult

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestImageComparator:
    """Test ImageComparator orchestration."""

    def test_comparator_initialization(self, valid_config):
        """ImageComparator should initialize with config and create directories."""
        logger.debug("Testing ImageComparator initialization")
        comparator = ImageComparator(valid_config)

        assert comparator.config == valid_config
        assert comparator.analyzer_registry is not None
        assert comparator.processor is not None
        assert comparator.report_generator is not None
        assert valid_config.diff_path.exists()
        assert valid_config.html_path.exists()

        logger.info("✓ ImageComparator initialization test passed")

    def test_find_images_flat_directory(self, temp_image_dir, simple_test_image):
        """_find_images should find images in flat directory structure."""
        logger.debug("Testing _find_images with flat directory")

        # Create test directory with images
        test_dir = temp_image_dir / "test_flat"
        test_dir.mkdir()
        simple_test_image.save(test_dir / "image1.png")
        simple_test_image.save(test_dir / "image2.jpg")
        simple_test_image.save(test_dir / "image3.PNG")  # Test case insensitivity

        # Create a config and comparator
        config = Config(
            base_dir=temp_image_dir,
            new_dir="test_flat",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        # Find images
        images = comparator._find_images(test_dir)

        assert len(images) == 3
        assert all(img.exists() for img in images)
        assert all(img.suffix.lower() in ImageComparator.IMAGE_EXTENSIONS for img in images)

        logger.info("✓ _find_images flat directory test passed")

    def test_find_images_nested_directory(self, temp_image_dir, simple_test_image):
        """_find_images should recursively find images in nested structure."""
        logger.debug("Testing _find_images with nested directory")

        # Create nested directory structure
        test_dir = temp_image_dir / "test_nested"
        subdir1 = test_dir / "subdir1"
        subdir2 = test_dir / "subdir2" / "deeper"
        subdir1.mkdir(parents=True)
        subdir2.mkdir(parents=True)

        # Save images at different levels
        simple_test_image.save(test_dir / "root.png")
        simple_test_image.save(subdir1 / "sub1.png")
        simple_test_image.save(subdir2 / "deep.jpg")

        # Create config and comparator
        config = Config(
            base_dir=temp_image_dir,
            new_dir="test_nested",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        # Find images
        images = comparator._find_images(test_dir)

        assert len(images) == 3
        assert any(img.name == "root.png" for img in images)
        assert any(img.name == "sub1.png" for img in images)
        assert any(img.name == "deep.jpg" for img in images)

        logger.info("✓ _find_images nested directory test passed")

    def test_find_images_empty_directory(self, temp_image_dir):
        """_find_images should return empty list for empty directory."""
        logger.debug("Testing _find_images with empty directory")

        test_dir = temp_image_dir / "empty"
        test_dir.mkdir()

        config = Config(
            base_dir=temp_image_dir,
            new_dir="empty",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        images = comparator._find_images(test_dir)

        assert images == []

        logger.info("✓ _find_images empty directory test passed")

    def test_find_images_nonexistent_directory(self, temp_image_dir):
        """_find_images should return empty list for nonexistent directory."""
        logger.debug("Testing _find_images with nonexistent directory")

        nonexistent_dir = temp_image_dir / "does_not_exist"

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        images = comparator._find_images(nonexistent_dir)

        assert images == []

        logger.info("✓ _find_images nonexistent directory test passed")

    def test_compare_single_pair_creates_outputs(self, valid_config, simple_test_image, simple_test_image_modified):
        """_compare_single_pair should create diff and annotated images."""
        logger.debug("Testing _compare_single_pair output creation")

        # Save test images
        new_path = valid_config.new_path / "test.png"
        known_path = valid_config.known_good_path / "test.png"
        simple_test_image_modified.save(new_path)
        simple_test_image.save(known_path)

        comparator = ImageComparator(valid_config)
        result = comparator._compare_single_pair(new_path, known_path)

        # Verify result is a ComparisonResult
        assert isinstance(result, ComparisonResult)
        assert result.filename == "test.png"
        assert result.new_image_path == new_path
        assert result.known_good_path == known_path

        # Verify diff and annotated images were created
        assert result.diff_image_path.exists()
        assert result.annotated_image_path.exists()

        # Verify metrics were generated
        assert result.metrics is not None
        assert 'Pixel Difference' in result.metrics
        assert result.percent_different >= 0

        # Verify histogram data was generated
        assert result.histogram_data is not None
        assert len(result.histogram_data) > 0

        logger.info("✓ _compare_single_pair output creation test passed")

    def test_compare_all_with_matching_files(self, temp_image_dir, simple_test_image, simple_test_image_modified):
        """compare_all should find and compare matching images."""
        logger.debug("Testing compare_all with matching files")

        # Create directory structure
        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_dir.mkdir()

        # Save matching images
        simple_test_image_modified.save(new_dir / "test1.png")
        simple_test_image.save(known_dir / "test1.png")

        simple_test_image_modified.save(new_dir / "test2.jpg")
        simple_test_image.save(known_dir / "test2.jpg")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        results = comparator.compare_all()

        assert len(results) == 2
        assert all(isinstance(r, ComparisonResult) for r in results)
        assert {r.filename for r in results} == {"test1.png", "test2.jpg"}

        # Results should be sorted by percent_different (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].percent_different >= results[i + 1].percent_different

        logger.info("✓ compare_all with matching files test passed")

    def test_compare_all_with_nested_structure(self, temp_image_dir, simple_test_image):
        """compare_all should preserve directory structure when matching."""
        logger.debug("Testing compare_all with nested structure")

        # Create nested directory structure
        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"

        new_subdir = new_dir / "subdir"
        known_subdir = known_dir / "subdir"

        new_subdir.mkdir(parents=True)
        known_subdir.mkdir(parents=True)

        # Save images preserving structure
        simple_test_image.save(new_subdir / "nested.png")
        simple_test_image.save(known_subdir / "nested.png")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        results = comparator.compare_all()

        assert len(results) == 1
        assert results[0].filename == "nested.png"
        # Should have found the matching file in the same relative path
        assert results[0].known_good_path == known_subdir / "nested.png"

        logger.info("✓ compare_all with nested structure test passed")

    def test_compare_all_filename_fallback(self, temp_image_dir, simple_test_image):
        """compare_all should fallback to filename matching when relative path doesn't match."""
        logger.debug("Testing compare_all filename fallback")

        # Create mismatched directory structure
        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"

        new_subdir = new_dir / "different_path"
        known_subdir = known_dir / "another_path"

        new_subdir.mkdir(parents=True)
        known_subdir.mkdir(parents=True)

        # Save images with same name but different paths
        simple_test_image.save(new_subdir / "image.png")
        simple_test_image.save(known_subdir / "image.png")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        results = comparator.compare_all()

        # Should still find the matching file by filename
        assert len(results) == 1
        assert results[0].filename == "image.png"

        logger.info("✓ compare_all filename fallback test passed")

    def test_compare_all_no_matches(self, temp_image_dir, simple_test_image):
        """compare_all should handle case where no matching known good images exist."""
        logger.debug("Testing compare_all with no matches")

        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_dir.mkdir()

        # Only save in new directory
        simple_test_image.save(new_dir / "orphan.png")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        results = comparator.compare_all()

        # Should return empty results since no matches
        assert len(results) == 0

        logger.info("✓ compare_all with no matches test passed")

    def test_compare_all_empty_new_directory(self, temp_image_dir):
        """compare_all should return empty list when new directory is empty."""
        logger.debug("Testing compare_all with empty new directory")

        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_dir.mkdir()

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        results = comparator.compare_all()

        assert results == []

        logger.info("✓ compare_all with empty new directory test passed")

    def test_clean_output_directories(self, valid_config):
        """_clean_output_directories should remove and recreate directories."""
        logger.debug("Testing _clean_output_directories")

        comparator = ImageComparator(valid_config)

        # Create some files in output directories
        test_diff = valid_config.diff_path / "test.png"
        test_report = valid_config.html_path / "test.html"

        test_diff.write_text("test")
        test_report.write_text("test")

        assert test_diff.exists()
        assert test_report.exists()

        # Clean directories
        comparator._clean_output_directories()

        # Files should be gone but directories should exist
        assert not test_diff.exists()
        assert not test_report.exists()
        assert valid_config.diff_path.exists()
        assert valid_config.html_path.exists()

        logger.info("✓ _clean_output_directories test passed")

    def test_compare_all_generates_reports(self, temp_image_dir, simple_test_image, simple_test_image_modified):
        """compare_all should generate HTML and markdown reports."""
        logger.debug("Testing compare_all report generation")

        # Setup test images
        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_dir.mkdir()

        simple_test_image_modified.save(new_dir / "test.png")
        simple_test_image.save(known_dir / "test.png")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator = ImageComparator(config)

        results = comparator.compare_all()

        # Verify reports were generated
        assert (config.html_path / "summary.html").exists()  # Fixed: actual filename
        assert (config.html_path / "summary.md").exists()  # Fixed: actual filename
        assert (config.html_path / "results.json").exists()

        logger.info("✓ compare_all report generation test passed")

    def test_image_extensions_supported(self):
        """ImageComparator should support multiple image extensions."""
        logger.debug("Testing supported image extensions")

        expected_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}

        assert ImageComparator.IMAGE_EXTENSIONS == expected_extensions

        logger.info("✓ Image extensions test passed")

    def test_compare_all_parallel_config_enabled(self, temp_image_dir, simple_test_image, simple_test_image_modified):
        """When enable_parallel=True, should use parallel processing."""
        logger.debug("Testing parallel processing with enable_parallel=True")

        # Create test setup
        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_dir.mkdir()

        simple_test_image_modified.save(new_dir / "test1.png")
        simple_test_image.save(known_dir / "test1.png")
        simple_test_image.save(new_dir / "test2.png")
        simple_test_image.save(known_dir / "test2.png")

        config = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_parallel=True,
            max_workers=2
        )

        comparator = ImageComparator(config)
        results = comparator.compare_all_parallel()

        # Should return list of results
        assert isinstance(results, list)
        assert len(results) == 2

        # Results should be valid ComparisonResult objects
        for result in results:
            assert isinstance(result, ComparisonResult)
            assert result.filename is not None

        logger.info("✓ Parallel processing config test passed")

    def test_compare_all_parallel_worker_function(self, valid_config, simple_test_image, simple_test_image_modified):
        """_compare_pair_worker should process images correctly."""
        logger.debug("Testing _compare_pair_worker static function")

        # Save test images
        new_path = valid_config.new_path / "test.png"
        known_path = valid_config.known_good_path / "test.png"
        simple_test_image_modified.save(new_path)
        simple_test_image.save(known_path)

        # Serialize config for worker
        config_dict = {
            'base_dir': valid_config.base_dir,
            'new_dir': valid_config.new_dir,
            'known_good_dir': valid_config.known_good_dir,
            'diff_dir': valid_config.diff_dir,
            'html_dir': valid_config.html_dir,
            'pixel_diff_threshold': valid_config.pixel_diff_threshold,
            'pixel_change_threshold': valid_config.pixel_change_threshold,
            'ssim_threshold': valid_config.ssim_threshold,
            'color_distance_threshold': valid_config.color_distance_threshold,
            'min_contour_area': valid_config.min_contour_area,
            'use_histogram_equalization': valid_config.use_histogram_equalization,
            'use_clahe': valid_config.use_clahe,
            'equalize_to_grayscale': valid_config.equalize_to_grayscale,
            'highlight_color': valid_config.highlight_color,
            'diff_enhancement_factor': valid_config.diff_enhancement_factor,
        }

        # Call worker function
        result = ImageComparator._compare_pair_worker((config_dict, new_path, known_path))

        # Verify result
        assert result is not None
        assert isinstance(result, ComparisonResult)
        assert result.filename == "test.png"
        assert result.diff_image_path.exists()
        assert result.annotated_image_path.exists()

        logger.info("✓ Worker function test passed")

    def test_compare_all_parallel_vs_sequential_equivalence(self, temp_image_dir, simple_test_image, simple_test_image_modified):
        """Parallel and sequential processing should produce equivalent results."""
        logger.debug("Testing parallel vs sequential equivalence")

        # Create test setup
        new_dir = temp_image_dir / "new"
        known_dir = temp_image_dir / "known_good"
        new_dir.mkdir()
        known_dir.mkdir()

        simple_test_image_modified.save(new_dir / "test1.png")
        simple_test_image.save(known_dir / "test1.png")
        simple_test_image.save(new_dir / "test2.png")
        simple_test_image.save(known_dir / "test2.png")

        # Run sequential
        config_seq = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good"
        )
        comparator_seq = ImageComparator(config_seq)
        results_seq = comparator_seq.compare_all()

        # Clean for parallel run
        comparator_seq._clean_output_directories()

        # Run parallel
        config_par = Config(
            base_dir=temp_image_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_parallel=True,
            max_workers=2
        )
        comparator_par = ImageComparator(config_par)
        results_par = comparator_par.compare_all_parallel()

        # Should have same number of results
        assert len(results_seq) == len(results_par)

        # Sort both by filename for comparison
        seq_sorted = sorted(results_seq, key=lambda r: r.filename)
        par_sorted = sorted(results_par, key=lambda r: r.filename)

        # Should have same filenames and similar metrics
        for s_result, p_result in zip(seq_sorted, par_sorted):
            assert s_result.filename == p_result.filename
            # Metrics should be very close (allow small floating point differences)
            assert abs(s_result.percent_different - p_result.percent_different) < 0.01

        logger.info("✓ Parallel vs sequential equivalence test passed")
