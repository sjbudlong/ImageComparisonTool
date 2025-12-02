"""
Unit tests for ReportGenerator class.
"""

import pytest
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from report_generator import ReportGenerator
from config import Config
from models import ComparisonResult

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestReportGenerator:
    """Test ReportGenerator HTML report creation."""

    def test_report_generator_initialization(self, base_config):
        """ReportGenerator should initialize with config."""
        logger.debug("Testing ReportGenerator initialization")

        generator = ReportGenerator(base_config)

        assert generator.config == base_config

        logger.info("✓ ReportGenerator initialization test passed")

    def test_metric_descriptions_exist(self):
        """ReportGenerator should have metric descriptions."""
        logger.debug("Testing metric descriptions")

        assert "Pixel Difference" in ReportGenerator.METRIC_DESCRIPTIONS
        assert "Structural Similarity" in ReportGenerator.METRIC_DESCRIPTIONS
        assert "Histogram Analysis" in ReportGenerator.METRIC_DESCRIPTIONS

        logger.info("✓ Metric descriptions test passed")

    def test_generate_detail_report_creates_file(
        self, valid_config, simple_test_image, simple_test_image_modified
    ):
        """generate_detail_report should create HTML file."""
        logger.debug("Testing detail report generation")

        # Setup test images
        new_path = valid_config.new_path / "test.png"
        known_path = valid_config.known_good_path / "test.png"
        diff_path = valid_config.diff_path / "diff_test.png"
        annotated_path = valid_config.diff_path / "annotated_test.png"

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        simple_test_image_modified.save(new_path)
        simple_test_image.save(known_path)
        simple_test_image.save(diff_path)
        simple_test_image.save(annotated_path)

        # Create a comparison result
        result = ComparisonResult(
            filename="test.png",
            new_image_path=new_path,
            known_good_path=known_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics={"Pixel Difference": {"percent_different": 5.5}},
            percent_different=5.5,
            histogram_data="base64encodeddata",
        )

        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(result)

        # Verify file was created
        output_path = valid_config.html_path / "test.png.html"
        assert output_path.exists()

        # Verify content
        content = output_path.read_text(encoding="utf-8")
        assert "test.png" in content
        assert "5.5" in content

        logger.info("✓ Detail report generation test passed")

    def test_generate_summary_report_creates_file(
        self, valid_config, simple_test_image
    ):
        """generate_summary_report should create summary HTML with subdirectories."""
        logger.debug("Testing summary report generation")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        # Create test results - all in root directory
        results = []
        for i in range(3):
            new_path = valid_config.new_path / f"test{i}.png"
            known_path = valid_config.known_good_path / f"test{i}.png"
            diff_path = valid_config.diff_path / f"diff_test{i}.png"
            annotated_path = valid_config.diff_path / f"annotated_test{i}.png"

            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)

            result = ComparisonResult(
                filename=f"test{i}.png",
                new_image_path=new_path,
                known_good_path=known_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics={"Pixel Difference": {"percent_different": i * 2.0}},
                percent_different=i * 2.0,
                histogram_data="",
            )
            results.append(result)

        generator = ReportGenerator(valid_config)
        generator.generate_summary_report(results)

        # Verify file was created
        output_path = valid_config.html_path / "summary.html"
        assert output_path.exists()

        # Verify content - now shows subdirectories instead of individual files
        content = output_path.read_text(encoding="utf-8")
        assert "Image Comparison Summary" in content
        assert "3" in content  # Total count
        assert "Ungrouped" in content  # Root-level files shown as "Ungrouped"
        assert "Directory" in content  # Column header
        assert "subdir_root.html" in content  # Link to root subdirectory index

        logger.info("✓ Summary report generation test passed")

    def test_get_relative_path(self, valid_config):
        """_get_relative_path should compute relative paths correctly."""
        logger.debug("Testing relative path calculation")

        generator = ReportGenerator(valid_config)

        # Test with a file in diff directory
        diff_file = valid_config.diff_path / "test.png"
        rel_path = generator._get_relative_path(diff_file)

        # Should be relative to html_path
        assert ".." in rel_path or "diffs" in rel_path
        assert rel_path.replace("\\", "/").endswith("test.png")

        logger.info("✓ Relative path calculation test passed")

    def test_format_metrics(self, valid_config):
        """_format_metrics should create HTML from metrics dict."""
        logger.debug("Testing metrics formatting")

        generator = ReportGenerator(valid_config)

        metrics = {
            "Pixel Difference": {
                "percent_different": 5.5,
                "changed_pixels": 1000,
                "total_pixels": 10000,
            },
            "Structural Similarity": {
                "ssim_score": 0.95,
                "ssim_description": "Very similar",
            },
        }

        html = generator._format_metrics(metrics)

        assert "Pixel Difference" in html
        assert "Structural Similarity" in html
        assert "5.5" in html
        assert "0.95" in html
        assert "metric-group" in html

        logger.info("✓ Metrics formatting test passed")

    def test_format_key(self, valid_config):
        """_format_key should format keys nicely."""
        logger.debug("Testing key formatting")

        generator = ReportGenerator(valid_config)

        assert generator._format_key("percent_different") == "Percent Different"
        assert generator._format_key("ssim_score") == "Ssim Score"
        assert generator._format_key("test_key_name") == "Test Key Name"

        logger.info("✓ Key formatting test passed")

    def test_format_value(self, valid_config):
        """_format_value should format values appropriately."""
        logger.debug("Testing value formatting")

        generator = ReportGenerator(valid_config)

        # Test float formatting
        assert generator._format_value(5.123456) == "5.1235"
        assert (
            generator._format_value(0.9999) == "0.9999"
        )  # Fixed: actual output is 0.9999

        # Test other types
        assert generator._format_value(100) == "100"
        assert generator._format_value("test") == "test"
        assert generator._format_value((1, 2, 3)) == "(1, 2, 3)"

        logger.info("✓ Value formatting test passed")

    def test_get_status_class(self, valid_config):
        """_get_status_class should return correct CSS class."""
        logger.debug("Testing status class determination")

        generator = ReportGenerator(valid_config)

        assert generator._get_status_class(0.05) == "status-identical"
        assert generator._get_status_class(0.5) == "status-minor"
        assert generator._get_status_class(2.5) == "status-moderate"
        assert generator._get_status_class(10.0) == "status-major"

        logger.info("✓ Status class test passed")

    def test_get_status_text(self, valid_config):
        """_get_status_text should return correct status text."""
        logger.debug("Testing status text determination")

        generator = ReportGenerator(valid_config)

        assert generator._get_status_text(0.05) == "Nearly Identical"
        assert generator._get_status_text(0.5) == "Minor Differences"
        assert generator._get_status_text(2.5) == "Moderate Differences"
        assert generator._get_status_text(10.0) == "Major Differences"

        logger.info("✓ Status text test passed")

    def test_html_template_has_placeholders(self, valid_config):
        """_get_html_template should return valid template with placeholders."""
        logger.debug("Testing HTML template")

        generator = ReportGenerator(valid_config)
        template = generator._get_html_template()

        # Check for expected placeholders
        assert "{{TITLE}}" in template
        assert "{{FILENAME}}" in template
        assert "{{PERCENT_DIFF}}" in template
        assert "{{NEW_IMAGE}}" in template
        assert "{{KNOWN_GOOD_IMAGE}}" in template
        assert "{{DIFF_IMAGE}}" in template
        assert "{{ANNOTATED_IMAGE}}" in template
        assert "{{METRICS}}" in template
        assert "{{HISTOGRAM_DATA}}" in template

        # Check for valid HTML
        assert "<!DOCTYPE html>" in template
        assert "<html" in template
        assert "</html>" in template

        logger.info("✓ HTML template test passed")

    def test_summary_template_has_placeholders(self, valid_config):
        """_get_summary_template should return valid template."""
        logger.debug("Testing summary template")

        generator = ReportGenerator(valid_config)
        template = generator._get_summary_template()

        assert "{{TOTAL_COUNT}}" in template
        assert "{{ROWS}}" in template
        assert "<!DOCTYPE html>" in template
        assert "Image Comparison Summary" in template

        logger.info("✓ Summary template test passed")

    def test_navigation_links_in_detail_report(self, valid_config, simple_test_image):
        """Detail reports should include navigation links."""
        logger.debug("Testing navigation links")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        # Create multiple results
        results = []
        for i in range(3):
            new_path = valid_config.new_path / f"test{i}.png"
            known_path = valid_config.known_good_path / f"test{i}.png"
            diff_path = valid_config.diff_path / f"diff_test{i}.png"
            annotated_path = valid_config.diff_path / f"annotated_test{i}.png"

            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)

            result = ComparisonResult(
                filename=f"test{i}.png",
                new_image_path=new_path,
                known_good_path=known_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics={"Pixel Difference": {"percent_different": 1.0}},
                percent_different=1.0,
                histogram_data="",
            )
            results.append(result)

        generator = ReportGenerator(valid_config)

        # Generate report for middle result
        generator.generate_detail_report(results[1], results)

        # Check the generated HTML
        output_path = valid_config.html_path / "test1.png.html"
        content = output_path.read_text(encoding="utf-8")

        # Should have previous and next links
        assert "test0.png.html" in content  # Previous
        assert "test2.png.html" in content  # Next

        logger.info("✓ Navigation links test passed")

    def test_detail_report_without_navigation(self, valid_config, simple_test_image):
        """Detail report with single result should not have nav links."""
        logger.debug("Testing detail report without navigation")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        new_path = valid_config.new_path / "single.png"
        known_path = valid_config.known_good_path / "single.png"
        diff_path = valid_config.diff_path / "diff_single.png"
        annotated_path = valid_config.diff_path / "annotated_single.png"

        simple_test_image.save(new_path)
        simple_test_image.save(known_path)
        simple_test_image.save(diff_path)
        simple_test_image.save(annotated_path)

        result = ComparisonResult(
            filename="single.png",
            new_image_path=new_path,
            known_good_path=known_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics={"Pixel Difference": {"percent_different": 1.0}},
            percent_different=1.0,
            histogram_data="",
        )

        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(result, [result])

        output_path = valid_config.html_path / "single.png.html"
        content = output_path.read_text(encoding="utf-8")

        # Should have Back to Summary link but no prev/next
        assert "summary.html" in content
        # Navigation buttons for single result should be minimal
        assert content.count("← Previous") == 0 or content.count("Next →") == 0

        logger.info("✓ Detail report without navigation test passed")

    def test_metrics_with_descriptions(self, valid_config):
        """Metrics should include toggleable descriptions."""
        logger.debug("Testing metrics with descriptions")

        generator = ReportGenerator(valid_config)

        metrics = {"Pixel Difference": {"percent_different": 5.0}}

        html = generator._format_metrics(metrics)

        # Should have description functionality
        assert "metric-description" in html
        assert "toggleDescription" in html
        assert "pixel-difference" in html  # Group ID

        logger.info("✓ Metrics with descriptions test passed")

    def test_report_handles_missing_histogram_data(
        self, valid_config, simple_test_image
    ):
        """Report should handle missing histogram data gracefully."""
        logger.debug("Testing report with missing histogram data")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        new_path = valid_config.new_path / "no_histogram.png"
        known_path = valid_config.known_good_path / "no_histogram.png"
        diff_path = valid_config.diff_path / "diff_no_histogram.png"
        annotated_path = valid_config.diff_path / "annotated_no_histogram.png"

        simple_test_image.save(new_path)
        simple_test_image.save(known_path)
        simple_test_image.save(diff_path)
        simple_test_image.save(annotated_path)

        result = ComparisonResult(
            filename="no_histogram.png",
            new_image_path=new_path,
            known_good_path=known_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics={"Pixel Difference": {"percent_different": 1.0}},
            percent_different=1.0,
            histogram_data=None,  # No histogram
        )

        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(result)

        # Should still create the file
        output_path = valid_config.html_path / "no_histogram.png.html"
        assert output_path.exists()

        logger.info("✓ Report with missing histogram data test passed")

    def test_group_by_subdirectory(self, valid_config, simple_test_image):
        """_group_by_subdirectory should group results correctly."""
        logger.debug("Testing subdirectory grouping")

        # Create test results in different subdirectories
        results = []

        # Root level image
        root_path = valid_config.new_path / "root.png"
        simple_test_image.save(root_path)
        results.append(
            ComparisonResult(
                filename="root.png",
                new_image_path=root_path,
                known_good_path=Path("/known.png"),
                diff_image_path=Path("/diff.png"),
                annotated_image_path=Path("/annotated.png"),
                metrics={},
                percent_different=1.0,
                histogram_data="",
            )
        )

        # Subdirectory images
        ui_dir = valid_config.new_path / "ui"
        ui_dir.mkdir()
        for i in range(2):
            ui_path = ui_dir / f"ui{i}.png"
            simple_test_image.save(ui_path)
            results.append(
                ComparisonResult(
                    filename=f"ui{i}.png",
                    new_image_path=ui_path,
                    known_good_path=Path("/known.png"),
                    diff_image_path=Path("/diff.png"),
                    annotated_image_path=Path("/annotated.png"),
                    metrics={},
                    percent_different=float(i),
                    histogram_data="",
                )
            )

        generator = ReportGenerator(valid_config)
        grouped = generator._group_by_subdirectory(results)

        # Should have 2 groups: "" (root) and "ui"
        assert len(grouped) == 2
        assert "" in grouped
        assert "ui" in grouped
        assert len(grouped[""]) == 1
        assert len(grouped["ui"]) == 2

        # Results should be sorted by percent_different descending
        assert grouped["ui"][0].percent_different >= grouped["ui"][1].percent_different

        logger.info("✓ Subdirectory grouping test passed")

    def test_generate_subdirectory_index(self, valid_config, simple_test_image):
        """generate_subdirectory_index should create subdirectory index page."""
        logger.debug("Testing subdirectory index generation")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        # Create test results
        ui_dir = valid_config.new_path / "ui"
        ui_dir.mkdir()
        results = []

        for i in range(2):
            new_path = ui_dir / f"test{i}.png"
            known_path = valid_config.known_good_path / f"test{i}.png"
            diff_path = valid_config.diff_path / f"diff_test{i}.png"
            annotated_path = valid_config.diff_path / f"annotated_test{i}.png"

            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)

            results.append(
                ComparisonResult(
                    filename=f"test{i}.png",
                    new_image_path=new_path,
                    known_good_path=known_path,
                    diff_image_path=diff_path,
                    annotated_image_path=annotated_path,
                    metrics={},
                    percent_different=float(i),
                    histogram_data="",
                )
            )

        generator = ReportGenerator(valid_config)
        generator.generate_subdirectory_index("ui", results)

        # Verify file was created
        output_path = valid_config.html_path / "subdir_ui.html"
        assert output_path.exists()

        # Verify content
        content = output_path.read_text(encoding="utf-8")
        assert "ui" in content
        assert "test0.png" in content
        assert "test1.png" in content
        assert "thumbnail-row" in content  # CSS class for thumbnails
        assert "summary.html" in content  # Breadcrumb link to summary

        logger.info("✓ Subdirectory index generation test passed")

    def test_generate_subdirectory_index_root(self, valid_config, simple_test_image):
        """generate_subdirectory_index should handle root level (Ungrouped)."""
        logger.debug("Testing subdirectory index for root level")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        # Create root level result
        new_path = valid_config.new_path / "root.png"
        known_path = valid_config.known_good_path / "root.png"
        diff_path = valid_config.diff_path / "diff_root.png"
        annotated_path = valid_config.diff_path / "annotated_root.png"

        simple_test_image.save(new_path)
        simple_test_image.save(known_path)
        simple_test_image.save(diff_path)
        simple_test_image.save(annotated_path)

        result = ComparisonResult(
            filename="root.png",
            new_image_path=new_path,
            known_good_path=known_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics={},
            percent_different=1.0,
            histogram_data="",
        )

        generator = ReportGenerator(valid_config)
        generator.generate_subdirectory_index("", [result])

        # Verify file was created with "root" suffix
        output_path = valid_config.html_path / "subdir_root.html"
        assert output_path.exists()

        # Verify content shows "Ungrouped"
        content = output_path.read_text(encoding="utf-8")
        assert "Ungrouped" in content
        assert "root.png" in content

        logger.info("✓ Subdirectory index for root level test passed")

    def test_summary_report_with_subdirectories(self, valid_config, simple_test_image):
        """generate_summary_report should show subdirectory statistics."""
        logger.debug("Testing summary report with subdirectories")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        # Create results in different subdirectories
        results = []

        # Root level
        root_path = valid_config.new_path / "root.png"
        simple_test_image.save(root_path)
        results.append(
            ComparisonResult(
                filename="root.png",
                new_image_path=root_path,
                known_good_path=Path("/known.png"),
                diff_image_path=Path("/diff.png"),
                annotated_image_path=Path("/annotated.png"),
                metrics={},
                percent_different=1.0,
                histogram_data="",
            )
        )

        # UI subdirectory
        ui_dir = valid_config.new_path / "ui"
        ui_dir.mkdir()
        for i in range(2):
            ui_path = ui_dir / f"ui{i}.png"
            simple_test_image.save(ui_path)
            results.append(
                ComparisonResult(
                    filename=f"ui{i}.png",
                    new_image_path=ui_path,
                    known_good_path=Path("/known.png"),
                    diff_image_path=Path("/diff.png"),
                    annotated_image_path=Path("/annotated.png"),
                    metrics={},
                    percent_different=2.0 + i,
                    histogram_data="",
                )
            )

        generator = ReportGenerator(valid_config)
        generator.generate_summary_report(results)

        # Verify file was created
        output_path = valid_config.html_path / "summary.html"
        assert output_path.exists()

        # Verify content shows subdirectories
        content = output_path.read_text(encoding="utf-8")
        assert "Ungrouped" in content  # Root level
        assert "ui" in content  # Subdirectory
        assert "Directory" in content  # Column header
        assert "Images" in content  # Column header
        assert "subdir_root.html" in content  # Link to root index
        assert "subdir_ui.html" in content  # Link to ui index

        logger.info("✓ Summary report with subdirectories test passed")

    def test_detail_report_has_breadcrumb(self, valid_config, simple_test_image):
        """Detail report should include breadcrumb navigation."""
        logger.debug("Testing detail report breadcrumb")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        # Create a subdirectory result
        ui_dir = valid_config.new_path / "ui"
        ui_dir.mkdir()
        new_path = ui_dir / "test.png"
        known_path = valid_config.known_good_path / "test.png"
        diff_path = valid_config.diff_path / "diff_test.png"
        annotated_path = valid_config.diff_path / "annotated_test.png"

        simple_test_image.save(new_path)
        simple_test_image.save(known_path)
        simple_test_image.save(diff_path)
        simple_test_image.save(annotated_path)

        result = ComparisonResult(
            filename="test.png",
            new_image_path=new_path,
            known_good_path=known_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics={},
            percent_different=1.5,
            histogram_data="",
        )

        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(result)

        # Verify file was created
        output_path = valid_config.html_path / "test.png.html"
        assert output_path.exists()

        # Verify breadcrumb navigation
        content = output_path.read_text(encoding="utf-8")
        assert "breadcrumb" in content
        assert "Summary" in content
        assert "ui" in content
        assert "test.png" in content
        assert "subdir_ui.html" in content  # Link back to subdirectory
        assert "Back to Directory" in content

        logger.info("✓ Detail report breadcrumb test passed")

    def test_detail_report_has_image_navigation(self, valid_config, simple_test_image):
        """Detail report should include image navigation in overlay."""
        logger.debug("Testing detail report image navigation")

        # Ensure directories exist
        valid_config.diff_path.mkdir(parents=True, exist_ok=True)
        valid_config.html_path.mkdir(parents=True, exist_ok=True)

        new_path = valid_config.new_path / "test.png"
        known_path = valid_config.known_good_path / "test.png"
        diff_path = valid_config.diff_path / "diff_test.png"
        annotated_path = valid_config.diff_path / "annotated_test.png"

        simple_test_image.save(new_path)
        simple_test_image.save(known_path)
        simple_test_image.save(diff_path)
        simple_test_image.save(annotated_path)

        result = ComparisonResult(
            filename="test.png",
            new_image_path=new_path,
            known_good_path=known_path,
            diff_image_path=diff_path,
            annotated_image_path=annotated_path,
            metrics={},
            percent_different=1.5,
            histogram_data="",
        )

        generator = ReportGenerator(valid_config)
        generator.generate_detail_report(result)

        output_path = valid_config.html_path / "test.png.html"
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")

        # Check for navigation button functionality
        assert "previousImage()" in content
        assert "nextImage()" in content
        assert "overlayImages" in content
        assert "overlayLabels" in content
        assert "currentImageIndex" in content

        # Check for navigation button elements
        assert 'id="prev-btn"' in content
        assert 'id="next-btn"' in content
        assert 'id="overlay-counter"' in content

        # Check for keyboard navigation
        assert "ArrowLeft" in content
        assert "ArrowRight" in content

        # Check for all image labels
        assert "'Known Good'" in content
        assert "'New'" in content
        assert "'Diff'" in content
        assert "'Annotated'" in content

        logger.info("✓ Detail report image navigation test passed")
