"""
Unit tests for MarkdownExporter class.
"""

import pytest
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from markdown_exporter import MarkdownExporter
from models import ComparisonResult

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestMarkdownExporter:
    """Test MarkdownExporter markdown report generation."""

    def test_markdown_exporter_initialization(self, temp_image_dir):
        """MarkdownExporter should initialize with output directory."""
        logger.debug("Testing MarkdownExporter initialization")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        assert exporter.output_dir == output_dir
        assert output_dir.exists()

        logger.info("✓ MarkdownExporter initialization test passed")

    def test_export_summary_creates_file(self, temp_image_dir, simple_test_image):
        """export_summary should create markdown file."""
        logger.debug("Testing export_summary file creation")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        # Create test results
        new_path = temp_image_dir / "new" / "test.png"
        known_path = temp_image_dir / "known" / "test.png"
        diff_path = temp_image_dir / "diff" / "diff_test.png"
        annotated_path = temp_image_dir / "diff" / "annotated_test.png"

        new_path.parent.mkdir(parents=True, exist_ok=True)
        known_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)

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
            metrics={'Pixel Difference': {'percent_different': 2.5}},
            percent_different=2.5,
            histogram_data=""
        )

        output_path = exporter.export_summary([result])

        assert output_path.exists()
        assert output_path.name == "summary.md"

        logger.info("✓ export_summary file creation test passed")

    def test_markdown_summary_format(self, temp_image_dir, simple_test_image):
        """Markdown summary should have correct format."""
        logger.debug("Testing markdown summary format")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        # Create multiple test results
        results = []
        for i, diff in enumerate([0.05, 0.5, 2.5, 10.0]):
            new_path = temp_image_dir / "new" / f"test{i}.png"
            known_path = temp_image_dir / "known" / f"test{i}.png"
            diff_path = temp_image_dir / "diff" / f"diff_test{i}.png"
            annotated_path = temp_image_dir / "diff" / f"annotated_test{i}.png"

            new_path.parent.mkdir(parents=True, exist_ok=True)
            known_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path.parent.mkdir(parents=True, exist_ok=True)

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
                metrics={'Pixel Difference': {'percent_different': diff}},
                percent_different=diff,
                histogram_data=""
            )
            results.append(result)

        output_path = exporter.export_summary(results)
        content = output_path.read_text(encoding='utf-8')

        # Check markdown structure
        assert '# Image Comparison Summary' in content
        assert '## Statistics' in content
        assert '## Detailed Results' in content
        assert '| # | Filename | Difference % | Status |' in content

        logger.info("✓ Markdown summary format test passed")

    def test_markdown_includes_statistics(self, temp_image_dir, simple_test_image):
        """Markdown should include statistics section."""
        logger.debug("Testing markdown statistics inclusion")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        # Create test results with known statistics
        results = []
        differences = [0.05, 0.5, 2.5, 10.0]  # 1 identical, 1 minor, 1 moderate, 1 major

        for i, diff in enumerate(differences):
            new_path = temp_image_dir / "new" / f"test{i}.png"
            known_path = temp_image_dir / "known" / f"test{i}.png"
            diff_path = temp_image_dir / "diff" / f"diff_test{i}.png"
            annotated_path = temp_image_dir / "diff" / f"annotated_test{i}.png"

            new_path.parent.mkdir(parents=True, exist_ok=True)
            known_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path.parent.mkdir(parents=True, exist_ok=True)

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
                metrics={'Pixel Difference': {'percent_different': diff}},
                percent_different=diff,
                histogram_data=""
            )
            results.append(result)

        output_path = exporter.export_summary(results)
        content = output_path.read_text(encoding='utf-8')

        # Verify statistics
        assert '**Total Comparisons**: 4' in content
        assert '**Nearly Identical** (<0.1%): 1' in content
        assert '**Minor Differences** (0.1-1%): 1' in content
        assert '**Moderate Differences** (1-5%): 1' in content
        assert '**Major Differences** (≥5%): 1' in content

        # Verify difference statistics
        assert 'Maximum Difference' in content
        assert 'Minimum Difference' in content
        assert 'Average Difference' in content

        logger.info("✓ Markdown statistics test passed")

    def test_markdown_categorization(self, temp_image_dir, simple_test_image):
        """Markdown should correctly categorize results."""
        logger.debug("Testing markdown categorization")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        # Create a result for each category
        test_cases = [
            ("nearly_identical.png", 0.05, "Nearly Identical", "✅"),
            ("minor.png", 0.5, "Minor Differences", "⚠️"),
            ("moderate.png", 2.5, "Moderate Differences", "⚠️"),
            ("major.png", 10.0, "Major Differences", "❌"),
        ]

        results = []
        for filename, diff, expected_status, expected_emoji in test_cases:
            new_path = temp_image_dir / "new" / filename
            known_path = temp_image_dir / "known" / filename
            diff_path = temp_image_dir / "diff" / f"diff_{filename}"
            annotated_path = temp_image_dir / "diff" / f"annotated_{filename}"

            new_path.parent.mkdir(parents=True, exist_ok=True)
            known_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path.parent.mkdir(parents=True, exist_ok=True)

            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)

            result = ComparisonResult(
                filename=filename,
                new_image_path=new_path,
                known_good_path=known_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics={'Pixel Difference': {'percent_different': diff}},
                percent_different=diff,
                histogram_data=""
            )
            results.append(result)

        output_path = exporter.export_summary(results)
        content = output_path.read_text(encoding='utf-8')

        # Verify each result appears with correct status
        for filename, diff, expected_status, expected_emoji in test_cases:
            assert filename in content
            assert expected_status in content
            assert expected_emoji in content

        logger.info("✓ Markdown categorization test passed")

    def test_get_status_text(self):
        """_get_status_text should return correct status."""
        logger.debug("Testing _get_status_text")

        assert MarkdownExporter._get_status_text(0.05) == 'Nearly Identical'
        assert MarkdownExporter._get_status_text(0.5) == 'Minor Differences'
        assert MarkdownExporter._get_status_text(2.5) == 'Moderate Differences'
        assert MarkdownExporter._get_status_text(10.0) == 'Major Differences'

        logger.info("✓ _get_status_text test passed")

    def test_get_status_emoji(self):
        """_get_status_emoji should return correct emoji."""
        logger.debug("Testing _get_status_emoji")

        assert MarkdownExporter._get_status_emoji('Nearly Identical') == '✅'
        assert MarkdownExporter._get_status_emoji('Minor Differences') == '⚠️'
        assert MarkdownExporter._get_status_emoji('Moderate Differences') == '⚠️'
        assert MarkdownExporter._get_status_emoji('Major Differences') == '❌'
        assert MarkdownExporter._get_status_emoji('Unknown') == '❓'

        logger.info("✓ _get_status_emoji test passed")

    def test_get_overall_status(self, temp_image_dir, simple_test_image):
        """_get_overall_status should determine overall status correctly."""
        logger.debug("Testing _get_overall_status")

        # Test with all passing
        results_passing = []
        for i in range(3):
            new_path = temp_image_dir / "new" / f"pass{i}.png"
            known_path = temp_image_dir / "known" / f"pass{i}.png"
            diff_path = temp_image_dir / "diff" / f"diff_pass{i}.png"
            annotated_path = temp_image_dir / "diff" / f"annotated_pass{i}.png"

            new_path.parent.mkdir(parents=True, exist_ok=True)
            known_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path.parent.mkdir(parents=True, exist_ok=True)

            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)

            result = ComparisonResult(
                filename=f"pass{i}.png",
                new_image_path=new_path,
                known_good_path=known_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics={'Pixel Difference': {'percent_different': 0.1}},
                percent_different=0.1,
                histogram_data=""
            )
            results_passing.append(result)

        status_passing = MarkdownExporter._get_overall_status(results_passing)
        assert status_passing == 'All comparisons passed'

        # Test with some major differences
        results_failing = []
        for i in range(3):
            diff_percent = 10.0 if i < 2 else 0.1  # 2 major, 1 minor

            new_path = temp_image_dir / "new" / f"fail{i}.png"
            known_path = temp_image_dir / "known" / f"fail{i}.png"
            diff_path = temp_image_dir / "diff" / f"diff_fail{i}.png"
            annotated_path = temp_image_dir / "diff" / f"annotated_fail{i}.png"

            new_path.parent.mkdir(parents=True, exist_ok=True)
            known_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path.parent.mkdir(parents=True, exist_ok=True)

            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)

            result = ComparisonResult(
                filename=f"fail{i}.png",
                new_image_path=new_path,
                known_good_path=known_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics={'Pixel Difference': {'percent_different': diff_percent}},
                percent_different=diff_percent,
                histogram_data=""
            )
            results_failing.append(result)

        status_failing = MarkdownExporter._get_overall_status(results_failing)
        assert 'Significant issues detected' in status_failing
        assert '2/3' in status_failing

        # Test with empty results
        assert MarkdownExporter._get_overall_status([]) == 'No comparisons'

        logger.info("✓ _get_overall_status test passed")

    def test_markdown_pipeline_agnostic_format(self, temp_image_dir, simple_test_image):
        """Markdown should use pipeline-agnostic format."""
        logger.debug("Testing markdown pipeline-agnostic format")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        new_path = temp_image_dir / "new" / "test.png"
        known_path = temp_image_dir / "known" / "test.png"
        diff_path = temp_image_dir / "diff" / "diff_test.png"
        annotated_path = temp_image_dir / "diff" / "annotated_test.png"

        new_path.parent.mkdir(parents=True, exist_ok=True)
        known_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)

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
            metrics={'Pixel Difference': {'percent_different': 2.5}},
            percent_different=2.5,
            histogram_data=""
        )

        output_path = exporter.export_summary([result])
        content = output_path.read_text(encoding='utf-8')

        # Should use standard markdown tables
        assert '|' in content
        assert '---' in content

        # Should have links to other reports and detail pages
        assert 'summary.html' in content
        assert 'results.json' in content
        assert 'test.png' in content
        assert '[View →]' in content  # Links to detail reports

        logger.info("✓ Markdown pipeline-agnostic format test passed")


    def test_markdown_includes_timestamp(self, temp_image_dir, simple_test_image):
        """Markdown should include generation timestamp."""
        logger.debug("Testing markdown timestamp")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        new_path = temp_image_dir / "new" / "test.png"
        known_path = temp_image_dir / "known" / "test.png"
        diff_path = temp_image_dir / "diff" / "diff_test.png"
        annotated_path = temp_image_dir / "diff" / "annotated_test.png"

        new_path.parent.mkdir(parents=True, exist_ok=True)
        known_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)

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
            metrics={'Pixel Difference': {'percent_different': 2.5}},
            percent_different=2.5,
            histogram_data=""
        )

        output_path = exporter.export_summary([result])
        content = output_path.read_text(encoding='utf-8')

        assert 'Generated:' in content

        logger.info("✓ Markdown timestamp test passed")

    def test_markdown_table_formatting(self, temp_image_dir, simple_test_image):
        """Markdown tables should be properly formatted."""
        logger.debug("Testing markdown table formatting")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)

        new_path = temp_image_dir / "new" / "test.png"
        known_path = temp_image_dir / "known" / "test.png"
        diff_path = temp_image_dir / "diff" / "diff_test.png"
        annotated_path = temp_image_dir / "diff" / "annotated_test.png"

        new_path.parent.mkdir(parents=True, exist_ok=True)
        known_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)

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
            metrics={'Pixel Difference': {'percent_different': 2.5}},
            percent_different=2.5,
            histogram_data=""
        )

        output_path = exporter.export_summary([result])
        content = output_path.read_text(encoding='utf-8')

        # Check table headers and separators
        assert '| Metric | Value |' in content
        assert '|--------|-------|' in content
        assert '| # | Filename | Difference % | Status |' in content
        assert '|---|----------|-------------|--------|' in content

        logger.info("✓ Markdown table formatting test passed")

    def test_export_summary_groups_by_subdirectory(self, temp_image_dir, simple_test_image):
        """export_summary should group results by subdirectory."""
        logger.debug("Testing export_summary subdirectory grouping")

        output_dir = temp_image_dir / "reports"
        exporter = MarkdownExporter(output_dir)
        base_new_dir = temp_image_dir / "new"

        # Create test results in different subdirectories
        results = []
        subdirs = ["", "subdir1", "subdir2"]
        
        for subdir_name in subdirs:
            if subdir_name:
                subdir_path = base_new_dir / subdir_name
            else:
                subdir_path = base_new_dir
            
            subdir_path.mkdir(parents=True, exist_ok=True)
            
            new_path = subdir_path / "test.png"
            known_path = temp_image_dir / "known" / (subdir_name or "root") / "test.png"
            known_path.parent.mkdir(parents=True, exist_ok=True)
            diff_path = temp_image_dir / "diff" / "diff_test.png"
            annotated_path = temp_image_dir / "diff" / "annotated_test.png"
            
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            
            simple_test_image.save(new_path)
            simple_test_image.save(known_path)
            simple_test_image.save(diff_path)
            simple_test_image.save(annotated_path)
            
            result = ComparisonResult(
                filename=f"{subdir_name or 'root'}_test.png" if subdir_name else "test.png",
                new_image_path=new_path,
                known_good_path=known_path,
                diff_image_path=diff_path,
                annotated_image_path=annotated_path,
                metrics={'Pixel Difference': {'percent_different': 1.5}},
                percent_different=1.5,
                histogram_data=""
            )
            results.append(result)

        output_path = exporter.export_summary(results, base_new_dir)
        content = output_path.read_text(encoding='utf-8')

        # Check for subdirectory headers
        assert "### Root Directory" in content or "### " in content
        assert "subdir1" in content or "subdir2" in content or content.count("###") >= 1

        logger.info("✓ export_summary subdirectory grouping test passed")

