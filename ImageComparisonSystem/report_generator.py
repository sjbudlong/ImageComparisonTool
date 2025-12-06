"""
HTML report generation for image comparison results.

Provides functionality to generate detailed HTML reports for individual
image comparisons and summary pages showing all results.
"""

import logging
from pathlib import Path
from typing import List, Optional
import numpy as np

# Handle both package and direct module imports
try:
    from .config import Config
    from .models import ComparisonResult
    from .processor import ImageProcessor
except ImportError:
    from config import Config  # type: ignore
    from models import ComparisonResult  # type: ignore
    from processor import ImageProcessor  # type: ignore

# Try to import visualization module (optional)
try:
    from .visualization import TrendChartGenerator
except ImportError:
    try:
        from visualization import TrendChartGenerator  # type: ignore
    except (ImportError, ValueError):
        TrendChartGenerator = None  # type: ignore

logger = logging.getLogger("ImageComparison")


class ReportGenerator:
    """Generates HTML reports for comparison results.

    Creates detailed HTML reports for each image comparison and a summary
    page with navigation and statistics.
    """

    # Metric descriptions for tooltips
    METRIC_DESCRIPTIONS = {
        "Pixel Difference": (
            "Compares pixel-by-pixel differences between images. "
            "Shows the percentage of pixels that differ and average RGB distance."
        ),
        "Structural Similarity": (
            "Measures structural similarity (SSIM) between images on a scale of 0-1. "
            "Higher values indicate more similar images. "
            "Accounts for luminance, contrast, and structure."
        ),
        "Histogram Analysis": (
            "Analyzes the distribution of color and brightness values. "
            "Compares histograms for each color channel (RGB). "
            "Useful for detecting lighting or contrast changes."
        ),
        "FLIP Perceptual Metric": (
            "NVIDIA FLIP (FLaws in Luminance and Pixels) is an advanced perceptual metric "
            "that closely matches human visual perception. Accounts for spatial frequency sensitivity, "
            "viewing distance, luminance adaptation, and chrominance. "
            "Values range from 0 (imperceptible differences) to 1 (significant perceptual differences). "
            "Superior to SSIM for rendering quality assessment and VFX/gaming workflows."
        ),
    }

    def __init__(self, config: Config, history_manager=None) -> None:
        """Initialize report generator.

        Args:
            config: Configuration object with output paths
            history_manager: Optional HistoryManager for trend chart data
        """
        self.config: Config = config
        self.history_manager = history_manager

        # Initialize chart generator if available
        self.chart_generator = None
        if TrendChartGenerator is not None:
            try:
                self.chart_generator = TrendChartGenerator(figsize=(10, 5), dpi=100)
                logger.debug("TrendChartGenerator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize chart generator: {e}")
                self.chart_generator = None

    def generate_detail_report(
        self, result: ComparisonResult, results: Optional[List[ComparisonResult]] = None
    ) -> None:
        """Generate detailed HTML report for a single comparison.

        Creates an HTML file with comparison details including side-by-side
        images, diff visualization, metrics, and navigation links.

        Args:
            result: Comparison result to generate report for
            results: Optional list of all results for navigation links
        """
        output_path: Path = self.config.html_path / f"{result.filename}.html"

        try:
            # Get relative paths for images (relative to the HTML output directory)
            new_img_rel: str = self._get_relative_path(result.new_image_path)
            known_good_rel: str = self._get_relative_path(result.known_good_path)
            diff_rel: str = self._get_relative_path(result.diff_image_path)
            annotated_rel: str = self._get_relative_path(result.annotated_image_path)

            # Get subdirectory for breadcrumb and back link
            subdir = result.get_subdirectory(self.config.new_path)
            if subdir:
                safe_subdir = subdir.replace("/", "_").replace("\\", "_")
                subdir_link = f"subdir_{safe_subdir}.html"
                breadcrumb_middle = f'<a href="{subdir_link}">{subdir}</a>'
            else:
                subdir_link = "subdir_root.html"
                breadcrumb_middle = '<a href="subdir_root.html">Ungrouped</a>'

            # Generate navigation links
            prev_link: str = ""
            next_link: str = ""
            if results and len(results) > 1:
                # Find current result index
                try:
                    current_idx: int = next(
                        i
                        for i, r in enumerate(results)
                        if r.filename == result.filename
                    )

                    # Previous link
                    if current_idx > 0:
                        prev_result: ComparisonResult = results[current_idx - 1]
                        prev_link = f'<a href="{prev_result.filename}.html" class="btn">← Previous</a>'

                    # Next link
                    if current_idx < len(results) - 1:
                        next_result: ComparisonResult = results[current_idx + 1]
                        next_link = f'<a href="{next_result.filename}.html" class="btn">Next →</a>'
                except StopIteration:
                    pass

            # Generate historical section if available
            historical_data = None
            if self.history_manager and hasattr(result, 'composite_score') and result.composite_score is not None:
                try:
                    # Get subdirectory for this result
                    subdirectory = result.get_subdirectory(self.config.new_path)

                    # Query historical data for trend charts
                    history_records = self.history_manager.get_history_for_image(
                        result.filename,
                        subdirectory=subdirectory if subdirectory else None,
                        limit=50  # Last 50 runs for trend visualization
                    )

                    # Format for trend chart: list of dicts with 'timestamp' and 'composite_score'
                    historical_data = [
                        {
                            'timestamp': h['timestamp'],
                            'composite_score': h['composite_score']
                        }
                        for h in history_records
                        if h.get('composite_score') is not None
                    ]

                    logger.debug(f"Retrieved {len(historical_data)} historical data points for {result.filename}")
                except Exception as e:
                    logger.warning(f"Failed to retrieve historical data for {result.filename}: {e}")
                    historical_data = None

            historical_section = self._generate_historical_section(result, historical_data=historical_data)

            # Generate FLIP section if available
            flip_section = self._generate_flip_section(result)

            # Generate histogram section (conditional on config)
            histogram_section = ""
            if self.config.show_histogram_visualization and result.histogram_data:
                histogram_section = f'''
                <div class="metrics">
                    <h2>Histogram Comparison</h2>
                    <img src="data:image/png;base64,{result.histogram_data}" alt="Histograms" style="width: 100%; max-width: 1000px; margin: 20px 0;">
                </div>
                '''

            html: str = self._get_html_template()
            html = html.replace("{{TITLE}}", f"Comparison: {result.filename}")
            html = html.replace("{{FILENAME}}", result.filename)
            html = html.replace("{{PERCENT_DIFF}}", f"{result.percent_different:.4f}")
            html = html.replace("{{NEW_IMAGE}}", new_img_rel)
            html = html.replace("{{KNOWN_GOOD_IMAGE}}", known_good_rel)
            html = html.replace("{{DIFF_IMAGE}}", diff_rel)
            html = html.replace("{{ANNOTATED_IMAGE}}", annotated_rel)
            html = html.replace("{{METRICS}}", self._format_metrics(result.metrics))
            html = html.replace("{{FLIP_SECTION}}", flip_section)
            html = html.replace("{{HISTOGRAM_SECTION}}", histogram_section)
            html = html.replace("{{HISTORICAL_SECTION}}", historical_section)
            html = html.replace("{{BREADCRUMB_MIDDLE}}", breadcrumb_middle)
            html = html.replace("{{SUBDIR_LINK}}", subdir_link)
            html = html.replace("{{PREV_LINK}}", prev_link)
            html = html.replace("{{NEXT_LINK}}", next_link)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"Generated report: {output_path.name}")
        except Exception as e:
            logger.error(
                f"Error generating report for {result.filename}: {e}", exc_info=True
            )

    def generate_summary_report(self, results: List[ComparisonResult]):
        """Generate summary HTML report listing all comparisons grouped by subdirectory."""
        output_path = self.config.html_path / "summary.html"

        try:
            # Group results by subdirectory
            grouped = self._group_by_subdirectory(results)

            # Sort subdirectories: empty string (root) first, then alphabetically
            sorted_subdirs = sorted(grouped.keys(), key=lambda x: (x != "", x))

            rows_html = []
            for idx, subdir in enumerate(sorted_subdirs):
                subdir_results = grouped[subdir]

                # Calculate statistics
                image_count = len(subdir_results)
                avg_diff = (
                    sum(r.percent_different for r in subdir_results) / image_count
                )
                max_diff = max(r.percent_different for r in subdir_results)

                # Calculate composite score statistics if available
                composite_scores = [
                    r.composite_score for r in subdir_results
                    if hasattr(r, 'composite_score') and r.composite_score is not None
                ]
                avg_composite = (
                    sum(composite_scores) / len(composite_scores)
                    if composite_scores else None
                )

                # Count anomalies
                anomaly_count = sum(
                    1 for r in subdir_results
                    if hasattr(r, 'is_anomaly') and r.is_anomaly
                )

                # Determine status class based on max difference
                status_class = self._get_status_class(max_diff)

                # Display name and link
                if subdir:
                    display_name = subdir
                    safe_subdir = subdir.replace("/", "_").replace("\\", "_")
                    subdir_link = f"subdir_{safe_subdir}.html"
                else:
                    display_name = "Ungrouped"
                    subdir_link = "subdir_root.html"

                # Format composite score cell
                composite_cell = ""
                if avg_composite is not None:
                    composite_cell = f"{avg_composite:.1f}"
                else:
                    composite_cell = "N/A"

                # Format anomaly cell
                anomaly_cell = ""
                if anomaly_count > 0:
                    anomaly_cell = f'<span class="anomaly-count">{anomaly_count}</span>'
                else:
                    anomaly_cell = "0"

                row = f"""
                <tr class="{status_class}">
                    <td>{idx + 1}</td>
                    <td><a href="{subdir_link}">{display_name}</a></td>
                    <td>{image_count}</td>
                    <td>{avg_diff:.4f}%</td>
                    <td>{max_diff:.4f}%</td>
                    <td>{composite_cell}</td>
                    <td>{anomaly_cell}</td>
                    <td>
                        <a href="{subdir_link}" class="btn-view">View Directory</a>
                    </td>
                </tr>
            """
                rows_html.append(row)

            # Generate configuration section
            config_section = self._generate_config_section()

            summary_html = self._get_summary_template()
            summary_html = summary_html.replace("{{TOTAL_COUNT}}", str(len(results)))
            summary_html = summary_html.replace("{{ROWS}}", "\n".join(rows_html))
            summary_html = summary_html.replace("{{CONFIG_SECTION}}", config_section)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary_html)
            logger.info("Generated summary report: summary.html")
        except Exception as e:
            logger.error(f"Error generating summary report: {e}", exc_info=True)

    def generate_subdirectory_index(
        self, subdirectory: str, results: List[ComparisonResult]
    ) -> None:
        """Generate index page for a subdirectory showing all images with thumbnails.

        Creates an HTML page with thumbnail grid showing all comparison results
        in a subdirectory. Each entry displays 4 thumbnails (new, known_good,
        diff, annotated) in a horizontal row.

        Args:
            subdirectory: Subdirectory path (empty string for root)
            results: List of comparison results for this subdirectory
        """
        # Determine output filename
        if subdirectory:
            # Create safe filename from subdirectory path
            safe_subdir = subdirectory.replace("/", "_").replace("\\", "_")
            output_filename = f"subdir_{safe_subdir}.html"
            display_name = subdirectory
        else:
            output_filename = "subdir_root.html"
            display_name = "Ungrouped"

        output_path = self.config.html_path / output_filename

        try:
            # Generate comparison cards
            cards_html = []
            for result in results:
                # Get relative paths for images
                new_img_rel = self._get_relative_path(result.new_image_path)
                known_good_rel = self._get_relative_path(result.known_good_path)
                diff_rel = self._get_relative_path(result.diff_image_path)
                annotated_rel = self._get_relative_path(result.annotated_image_path)

                # Detail page link
                detail_link = f"{result.filename}.html"

                # Status class for styling
                status_class = self._get_status_class(result.percent_different)

                # Get anomaly badge if available
                anomaly_badge = self._get_anomaly_badge_html(result)

                # Composite score if available
                composite_info = ""
                if hasattr(result, 'composite_score') and result.composite_score is not None:
                    composite_info = f'<div class="composite-info">Score: {result.composite_score:.1f}/100</div>'

                # Build card HTML
                card = f"""
            <a href="{detail_link}" class="comparison-card {status_class}">
                <div class="card-header">
                    <div class="filename">{result.filename} {anomaly_badge}</div>
                    <div class="card-metrics">
                        <div class="diff-badge">{result.percent_different:.4f}% diff</div>
                        {composite_info}
                    </div>
                </div>
                <div class="thumbnail-row">
                    <div class="thumbnail-item">
                        <div class="thumbnail-label">New</div>
                        <img src="{new_img_rel}" alt="New">
                    </div>
                    <div class="thumbnail-item">
                        <div class="thumbnail-label">Known Good</div>
                        <img src="{known_good_rel}" alt="Known Good">
                    </div>
                    <div class="thumbnail-item">
                        <div class="thumbnail-label">Diff</div>
                        <img src="{diff_rel}" alt="Diff">
                    </div>
                    <div class="thumbnail-item">
                        <div class="thumbnail-label">Annotated</div>
                        <img src="{annotated_rel}" alt="Annotated">
                    </div>
                </div>
            </a>
            """
                cards_html.append(card)

            # Get template and replace placeholders
            html = self._get_subdirectory_index_template()
            html = html.replace("{{SUBDIRECTORY}}", display_name)
            html = html.replace("{{SUBDIRECTORY_DISPLAY}}", display_name)
            html = html.replace("{{BACK_TO_SUMMARY}}", "summary.html")
            html = html.replace("{{IMAGE_COUNT}}", str(len(results)))
            html = html.replace("{{PLURAL}}", "s" if len(results) != 1 else "")
            html = html.replace("{{COMPARISON_CARDS}}", "\n".join(cards_html))

            # Write file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

            logger.info(f"Generated subdirectory index: {output_filename}")

        except Exception as e:
            logger.error(
                f"Error generating subdirectory index for {subdirectory}: {e}",
                exc_info=True,
            )

    def _group_by_subdirectory(self, results: List[ComparisonResult]):
        """Group comparison results by subdirectory.

        Groups results based on their subdirectory structure within the
        new_images directory. Results are sorted within each group by
        percent_different (descending).

        Args:
            results: List of all comparison results

        Returns:
            Dictionary mapping subdirectory path to list of results.
            Empty string key represents root-level images.
        """
        from collections import defaultdict

        grouped = defaultdict(list)

        for result in results:
            subdir = result.get_subdirectory(self.config.new_path)
            grouped[subdir].append(result)

        # Sort each group by percent_different (descending)
        for subdir in grouped:
            grouped[subdir].sort(key=lambda x: x.percent_different, reverse=True)

        return dict(grouped)

    def _get_relative_path(self, path: Path) -> str:
        """Get relative path from HTML directory to image."""
        try:
            # Compute path relative to the HTML output directory so links work
            # regardless of where images are stored under the project.
            from os import path as _opath

            rel = _opath.relpath(str(path), start=str(self.config.html_path))
            return rel.replace("\\", "/")
        except Exception:
            return str(path)

    def _format_metrics(self, metrics: dict) -> str:
        """Format metrics dictionary as HTML with togglable descriptions."""
        html_parts = []

        for analyzer_name, analyzer_metrics in metrics.items():
            # Generate unique ID for this metric group
            group_id = analyzer_name.lower().replace(" ", "-")
            description = self.METRIC_DESCRIPTIONS.get(analyzer_name, "")

            html_parts.append('<div class="metric-group">')
            html_parts.append(
                f'<div class="metric-header" onclick="toggleDescription(\'{group_id}\')">'
            )
            html_parts.append(f"<h3>{analyzer_name}</h3>")
            if description:
                html_parts.append(
                    '<span class="metric-help-icon" title="Click to see description">?</span>'
                )
            html_parts.append("</div>")

            if description:
                html_parts.append(
                    f'<div class="metric-description" id="{group_id}-desc" style="display: none;">'
                )
                html_parts.append(f"<p>{description}</p>")
                html_parts.append("</div>")

            html_parts.append("<dl>")

            for key, value in analyzer_metrics.items():
                if key != "error":
                    formatted_value = self._format_value(value)
                    html_parts.append(f"<dt>{self._format_key(key)}</dt>")
                    html_parts.append(f"<dd>{formatted_value}</dd>")

            html_parts.append("</dl>")
            html_parts.append("</div>")

        return "\n".join(html_parts)

    def _format_key(self, key: str) -> str:
        """Format metric key for display."""
        return key.replace("_", " ").title()

    def _format_value(self, value) -> str:
        """Format metric value for display."""
        if isinstance(value, float):
            return f"{value:.4f}"
        elif isinstance(value, (tuple, list)):
            return str(value)
        else:
            return str(value)

    def _get_status_class(self, percent_diff: float) -> str:
        """Get CSS class based on difference percentage."""
        if percent_diff < 0.1:
            return "status-identical"
        elif percent_diff < 1.0:
            return "status-minor"
        elif percent_diff < 5.0:
            return "status-moderate"
        else:
            return "status-major"

    def _get_status_text(self, percent_diff: float) -> str:
        """Get status text based on difference percentage."""
        if percent_diff < 0.1:
            return "Nearly Identical"
        elif percent_diff < 1.0:
            return "Minor Differences"
        elif percent_diff < 5.0:
            return "Moderate Differences"
        else:
            return "Major Differences"

    def _get_nav_link(self, direction: str, result: ComparisonResult) -> str:
        """Generate navigation link HTML - deprecated, kept for compatibility."""
        # Navigation is now handled in generate_detail_report
        return ""

    def _generate_flip_section(self, result: ComparisonResult) -> str:
        """
        Generate HTML for FLIP perceptual metric visualization with tabbed colormaps.

        Creates a multi-panel visualization with colormap tabs if FLIP metrics
        are present in the result.

        Args:
            result: ComparisonResult with FLIP metrics

        Returns:
            HTML string for FLIP section, or empty string if FLIP not available
        """
        # Check if FLIP metrics are present and visualization is enabled
        if not self.config.show_flip_visualization:
            return ""

        if "FLIP Perceptual Metric" not in result.metrics:
            return ""

        flip_metrics = result.metrics["FLIP Perceptual Metric"]

        # Check if FLIP error map is available
        if "flip_error_map_array" not in flip_metrics:
            logger.warning(f"FLIP metrics present but no error map for {result.filename}")
            return ""

        # Load images
        try:
            from PIL import Image as PILImage
            img1 = np.array(PILImage.open(result.known_good_path))
            img2 = np.array(PILImage.open(result.new_image_path))
            flip_map = flip_metrics["flip_error_map_array"]
        except Exception as e:
            logger.error(f"Failed to load images for FLIP visualization: {e}")
            return ""

        # Generate FLIP comparisons for each colormap
        html_parts = []
        html_parts.append('<div class="metrics flip-section">')
        html_parts.append('<h2>FLIP Perceptual Analysis</h2>')

        # Add metric summary
        html_parts.append('<div class="flip-summary">')
        html_parts.append('<table class="flip-metrics-table">')
        html_parts.append('<tr>')
        html_parts.append(f'<th>Mean Error</th><td>{flip_metrics["flip_mean"]:.6f}</td>')
        html_parts.append(f'<th>Max Error</th><td>{flip_metrics["flip_max"]:.6f}</td>')
        html_parts.append('</tr><tr>')
        html_parts.append(f'<th>95th Percentile</th><td>{flip_metrics["flip_percentile_95"]:.6f}</td>')
        html_parts.append(f'<th>Quality</th><td><strong>{flip_metrics["flip_quality_description"]}</strong></td>')
        html_parts.append('</tr>')
        html_parts.append('</table>')
        html_parts.append('</div>')

        # Generate tabbed colormap interface
        html_parts.append('<div class="flip-colormap-tabs">')

        # Tab buttons
        html_parts.append('<div class="tab-buttons">')
        for i, colormap in enumerate(self.config.flip_colormaps):
            active_class = ' active' if colormap == self.config.flip_default_colormap else ''
            html_parts.append(
                f'<button class="tab-button{active_class}" '
                f'onclick="showFlipTab(\'{colormap}\')">{colormap.capitalize()}</button>'
            )
        html_parts.append('</div>')

        # Tab content
        for colormap in self.config.flip_colormaps:
            try:
                flip_img_b64 = ImageProcessor.generate_flip_comparison_image(
                    img1, img2, flip_map, colormap
                )
                display_style = 'block' if colormap == self.config.flip_default_colormap else 'none'

                html_parts.append(f'<div id="flip-tab-{colormap}" class="tab-content" style="display: {display_style};">')
                html_parts.append(
                    f'<img src="data:image/png;base64,{flip_img_b64}" '
                    f'alt="FLIP {colormap}" style="width: 100%; max-width: 1400px; margin: 10px 0;">'
                )
                html_parts.append('</div>')

            except Exception as e:
                logger.error(f"Failed to generate FLIP visualization for colormap {colormap}: {e}")

        html_parts.append('</div>')  # Close flip-colormap-tabs

        # Add JavaScript for tab switching
        html_parts.append('''
        <script>
        function showFlipTab(colormapName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');

            // Remove active class from all buttons
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));

            // Show selected tab
            const tabContent = document.getElementById('flip-tab-' + colormapName);
            if (tabContent) {
                tabContent.style.display = 'block';
            }

            // Add active class to clicked button
            event.target.classList.add('active');
        }
        </script>
        ''')

        html_parts.append('</div>')  # Close metrics flip-section

        return '\n'.join(html_parts)

    def _generate_historical_section(
        self, result: ComparisonResult, historical_data: Optional[List[dict]] = None
    ) -> str:
        """Generate HTML for historical metrics section.

        Args:
            result: Current comparison result with history fields
            historical_data: Optional list of historical data points for trend chart

        Returns:
            HTML string for historical section, or empty string if no history
        """
        # Check if result has historical data
        if not hasattr(result, 'composite_score') or result.composite_score is None:
            return ""

        html_parts = []
        html_parts.append('<div class="metrics historical-section">')
        html_parts.append('<h2>Historical Analysis</h2>')

        # Composite score with anomaly badge
        html_parts.append('<div class="history-summary">')
        html_parts.append('<div class="history-metric">')
        html_parts.append('<dt>Composite Score</dt>')

        # Add anomaly badge if flagged
        anomaly_badge = ""
        if hasattr(result, 'is_anomaly') and result.is_anomaly:
            anomaly_badge = ' <span class="anomaly-badge" title="Statistical anomaly detected">⚠️ ANOMALY</span>'

        html_parts.append(f'<dd class="composite-score">{result.composite_score:.2f}/100{anomaly_badge}</dd>')
        html_parts.append('</div>')

        # Composite score explanation with weights
        html_parts.append('<div class="composite-explanation">')
        html_parts.append('<p class="explanation-text"><strong>Composite Score</strong> is a weighted combination of multiple metrics:</p>')
        html_parts.append('<ul class="metric-weights">')

        # Get weights from config (default: 0.25 each)
        weights = getattr(self.config, 'composite_metric_weights', None)
        if not weights:
            weights = {
                'pixel_diff': 0.25,
                'ssim': 0.25,
                'color_distance': 0.25,
                'histogram': 0.25
            }

        html_parts.append(f'<li><strong>Pixel Difference:</strong> {weights.get("pixel_diff", 0.25) * 100:.0f}% weight</li>')
        html_parts.append(f'<li><strong>SSIM (Structural Similarity):</strong> {weights.get("ssim", 0.25) * 100:.0f}% weight</li>')
        html_parts.append(f'<li><strong>Color Distance:</strong> {weights.get("color_distance", 0.25) * 100:.0f}% weight</li>')
        html_parts.append(f'<li><strong>Histogram Correlation:</strong> {weights.get("histogram", 0.25) * 100:.0f}% weight</li>')
        html_parts.append('</ul>')
        html_parts.append('<p class="explanation-text"><em>Lower scores indicate better similarity (0 = identical, 100 = completely different)</em></p>')
        html_parts.append('</div>')

        # Historical statistics if available
        if hasattr(result, 'historical_mean') and result.historical_mean is not None:
            html_parts.append('<div class="history-stats">')
            html_parts.append('<dl class="history-stats-grid">')

            html_parts.append('<dt>Historical Mean</dt>')
            html_parts.append(f'<dd>{result.historical_mean:.2f}</dd>')

            if hasattr(result, 'historical_std_dev') and result.historical_std_dev is not None:
                html_parts.append('<dt>Standard Deviation</dt>')
                html_parts.append(f'<dd>{result.historical_std_dev:.2f}</dd>')

            if hasattr(result, 'std_dev_from_mean') and result.std_dev_from_mean is not None:
                html_parts.append('<dt>Deviation from Mean</dt>')
                deviation_class = "deviation-high" if abs(result.std_dev_from_mean) > 2.0 else "deviation-normal"
                html_parts.append(f'<dd class="{deviation_class}">{result.std_dev_from_mean:.2f}σ</dd>')

            html_parts.append('</dl>')
            html_parts.append('</div>')

        html_parts.append('</div>')

        # Generate trend chart if data available
        if self.chart_generator and historical_data and len(historical_data) >= 2:
            try:
                chart_base64 = self.chart_generator.generate_trend_chart(
                    historical_data=historical_data,
                    filename=result.filename,
                    title=f"Historical Trend: {result.filename}"
                )

                if chart_base64:
                    html_parts.append('<div class="trend-chart">')
                    html_parts.append('<h3>Composite Score Over Time</h3>')
                    html_parts.append(f'<img src="data:image/png;base64,{chart_base64}" alt="Trend Chart" style="width: 100%; max-width: 900px;">')
                    html_parts.append('</div>')
            except Exception as e:
                logger.debug(f"Failed to generate trend chart: {e}")

        html_parts.append('</div>')

        return "\n".join(html_parts)

    def _get_anomaly_badge_html(self, result: ComparisonResult) -> str:
        """Generate anomaly badge HTML for summary tables.

        Args:
            result: Comparison result to check for anomaly status

        Returns:
            HTML string with anomaly badge, or empty string
        """
        if hasattr(result, 'is_anomaly') and result.is_anomaly:
            return '<span class="anomaly-badge-small" title="Statistical anomaly">⚠️</span>'
        return ""

    def _generate_config_section(self) -> str:
        """Generate HTML section displaying run configuration and settings.

        Returns:
            HTML string with configuration details
        """
        html_parts = []
        html_parts.append('<div class="config-section">')
        html_parts.append('<h2>Run Configuration</h2>')
        html_parts.append('<div class="config-grid">')

        # Paths
        html_parts.append('<div class="config-group">')
        html_parts.append('<h3>Directories</h3>')
        html_parts.append('<dl class="config-list">')
        html_parts.append('<dt>Base Directory</dt>')
        html_parts.append(f'<dd><code>{self.config.base_dir}</code></dd>')
        html_parts.append('<dt>New Images</dt>')
        html_parts.append(f'<dd><code>{self.config.new_dir}</code></dd>')
        html_parts.append('<dt>Known Good Images</dt>')
        html_parts.append(f'<dd><code>{self.config.known_good_dir}</code></dd>')
        html_parts.append('</dl>')
        html_parts.append('</div>')

        # Comparison Settings
        html_parts.append('<div class="config-group">')
        html_parts.append('<h3>Comparison Settings</h3>')
        html_parts.append('<dl class="config-list">')
        html_parts.append('<dt>Pixel Diff Threshold</dt>')
        html_parts.append(f'<dd>{self.config.pixel_diff_threshold}%</dd>')
        html_parts.append('<dt>SSIM Threshold</dt>')
        html_parts.append(f'<dd>{self.config.ssim_threshold}</dd>')
        html_parts.append('<dt>Color Distance Threshold</dt>')
        html_parts.append(f'<dd>{self.config.color_distance_threshold}</dd>')
        html_parts.append('<dt>Histogram Equalization</dt>')
        html_parts.append(f'<dd>{"Enabled" if self.config.use_histogram_equalization else "Disabled"}</dd>')
        html_parts.append('</dl>')
        html_parts.append('</div>')

        # Features
        html_parts.append('<div class="config-group">')
        html_parts.append('<h3>Enabled Features</h3>')
        html_parts.append('<dl class="config-list">')
        html_parts.append('<dt>FLIP Analysis</dt>')
        html_parts.append(f'<dd>{"Enabled" if self.config.enable_flip else "Disabled"}</dd>')
        if self.config.enable_flip:
            html_parts.append('<dt>FLIP Pixels Per Degree</dt>')
            html_parts.append(f'<dd>{self.config.flip_pixels_per_degree}</dd>')
        html_parts.append('<dt>Historical Tracking</dt>')
        html_parts.append(f'<dd>{"Enabled" if self.config.enable_history else "Disabled"}</dd>')
        if self.config.enable_history and self.config.build_number:
            html_parts.append('<dt>Build Number</dt>')
            html_parts.append(f'<dd><code>{self.config.build_number}</code></dd>')
        html_parts.append('<dt>Parallel Processing</dt>')
        html_parts.append(f'<dd>{"Enabled" if self.config.enable_parallel else "Disabled"}</dd>')
        if self.config.enable_parallel:
            html_parts.append('<dt>Max Workers</dt>')
            html_parts.append(f'<dd>{self.config.max_workers}</dd>')
        html_parts.append('</dl>')
        html_parts.append('</div>')

        html_parts.append('</div>')  # config-grid
        html_parts.append('</div>')  # config-section

        return '\n'.join(html_parts)

    def _get_subdirectory_index_template(self) -> str:
        """Return HTML template for subdirectory index page.

        Creates a template showing all images in a subdirectory with thumbnails.
        Each entry displays 4 thumbnails in a horizontal row: new, known_good,
        diff, and annotated_diff images.
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{SUBDIRECTORY}} - Image Comparison</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Breadcrumb navigation */
        .breadcrumb {
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .breadcrumb a {
            color: #3498db;
            text-decoration: none;
        }
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        .breadcrumb span {
            color: #999;
            margin: 0 8px;
        }

        /* Header */
        header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .summary-info {
            color: #666;
            font-size: 1.1em;
        }

        /* Image comparison cards */
        .comparison-grid {
            display: grid;
            gap: 20px;
            margin-top: 20px;
        }
        .comparison-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .comparison-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* Status-based left border coloring */
        .comparison-card.status-identical { border-left: 4px solid #27ae60; }
        .comparison-card.status-minor { border-left: 4px solid #f39c12; }
        .comparison-card.status-moderate { border-left: 4px solid #e67e22; }
        .comparison-card.status-major { border-left: 4px solid #e74c3c; }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }
        .filename {
            font-weight: 600;
            font-size: 1.1em;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-metrics {
            display: flex;
            flex-direction: column;
            gap: 5px;
            align-items: flex-end;
        }
        .diff-badge {
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .composite-info {
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .anomaly-badge-small {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
        }

        /* Thumbnail grid - 4 images in a horizontal row */
        .thumbnail-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        .thumbnail-item {
            text-align: center;
        }
        .thumbnail-label {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
            font-weight: 500;
        }
        .thumbnail-item img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        /* Responsive design */
        @media (max-width: 1200px) {
            .thumbnail-row {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 600px) {
            .thumbnail-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Breadcrumb -->
        <nav class="breadcrumb">
            <a href="{{BACK_TO_SUMMARY}}">Summary</a>
            <span>›</span>
            <strong>{{SUBDIRECTORY_DISPLAY}}</strong>
        </nav>

        <!-- Header -->
        <header>
            <h1>{{SUBDIRECTORY_DISPLAY}}</h1>
            <div class="summary-info">
                {{IMAGE_COUNT}} image{{PLURAL}} in this directory
            </div>
        </header>

        <!-- Comparison Cards -->
        <div class="comparison-grid">
            {{COMPARISON_CARDS}}
        </div>
    </div>
</body>
</html>"""

    def _get_html_template(self) -> str:
        """Return HTML template for detail page."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .diff-percentage {
            font-size: 2em;
            color: #e74c3c;
            font-weight: bold;
        }
        .breadcrumb {
            margin: 15px 0;
            font-size: 0.95em;
            color: #666;
        }
        .breadcrumb a {
            color: #3498db;
            text-decoration: none;
        }
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        .breadcrumb-separator {
            margin: 0 8px;
            color: #999;
        }
        .nav-buttons {
            margin: 20px 0;
            display: flex;
            gap: 10px;
            justify-content: space-between;
            align-items: center;
        }
        .nav-left {
            display: flex;
            gap: 10px;
        }
        .nav-right {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            min-width: 140px;
            text-align: center;
        }
        .btn:hover { background: #2980b9; }
        .btn-back {
            background: #95a5a6;
        }
        .btn-back:hover {
            background: #7f8c8d;
        }
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .image-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .image-card h2 {
            margin-bottom: 10px;
            color: #2c3e50;
            font-size: 1.2em;
        }
        .image-card img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .image-card img:hover {
            transform: scale(1.02);
        }
        .metrics {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metrics h2 {
            margin-top: 0;
            margin-bottom: 15px;
            color: #2c3e50;
            font-size: 1.3em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        /* Historical Analysis Styles */
        .historical-section {
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .historical-section h2 {
            border-bottom-color: rgba(255,255,255,0.3);
            color: white;
        }
        .historical-section h3 {
            color: white;
            margin: 20px 0 10px 0;
        }
        .history-summary {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .history-metric {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 6px;
        }
        .history-metric dt {
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .composite-score {
            font-size: 2.5em;
            font-weight: bold;
            color: white;
            line-height: 1.2;
        }
        .anomaly-badge {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.4em;
            font-weight: bold;
            vertical-align: middle;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .anomaly-badge-small {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 5px;
        }
        .history-stats {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 6px;
        }
        .history-stats-grid {
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 10px;
        }
        .history-stats dt {
            color: rgba(255,255,255,0.8);
            font-weight: normal;
        }
        .history-stats dd {
            color: white;
            font-weight: bold;
            font-size: 1.1em;
        }
        .composite-explanation {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
            border-left: 4px solid rgba(255,255,255,0.4);
        }
        .explanation-text {
            color: rgba(255,255,255,0.95);
            margin: 0 0 10px 0;
            line-height: 1.6;
        }
        .metric-weights {
            list-style: none;
            padding: 0;
            margin: 15px 0;
        }
        .metric-weights li {
            color: rgba(255,255,255,0.9);
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric-weights li:last-child {
            border-bottom: none;
        }
        .metric-weights strong {
            color: white;
        }
        .deviation-high {
            color: #e74c3c !important;
            background: rgba(231,76,60,0.2);
            padding: 2px 8px;
            border-radius: 3px;
        }
        /* FLIP Section Styles */
        .flip-section {
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .flip-section h2 {
            border-bottom-color: rgba(255,255,255,0.3);
            color: white;
        }
        .flip-summary {
            margin-bottom: 20px;
        }
        .flip-metrics-table {
            width: 100%;
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            padding: 10px;
        }
        .flip-metrics-table th {
            text-align: left;
            color: rgba(255,255,255,0.8);
            font-weight: normal;
            padding: 8px 12px;
            font-size: 0.9em;
        }
        .flip-metrics-table td {
            text-align: left;
            color: white;
            font-weight: bold;
            padding: 8px 12px;
        }
        .flip-colormap-tabs {
            margin-top: 15px;
        }
        .tab-buttons {
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
            background: rgba(255,255,255,0.1);
            padding: 5px;
            border-radius: 6px;
        }
        .tab-button {
            flex: 1;
            padding: 10px 20px;
            border: none;
            background: rgba(255,255,255,0.1);
            color: white;
            cursor: pointer;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .tab-button:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-1px);
        }
        .tab-button.active {
            background: rgba(255,255,255,0.3);
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .tab-content {
            background: rgba(255,255,255,0.95);
            padding: 10px;
            border-radius: 6px;
        }
        .deviation-normal {
            color: #27ae60 !important;
        }
        .trend-chart {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        .trend-chart img {
            border-radius: 6px;
            background: white;
            padding: 10px;
        }
        .metric-group {
            margin-bottom: 20px;
        }
        .metric-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            user-select: none;
        }
        .metric-header h3 {
            color: #2c3e50;
            margin-bottom: 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #3498db;
            flex: 1;
        }
        .metric-help-icon {
            display: inline-block;
            width: 24px;
            height: 24px;
            margin-left: 10px;
            background: #3498db;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            flex-shrink: 0;
        }
        .metric-help-icon:hover {
            background: #2980b9;
            transform: scale(1.1);
        }
        .metric-description {
            background: #ecf0f1;
            border-left: 4px solid #3498db;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 0.95em;
            color: #555;
            line-height: 1.5;
        }
        .metric-description p {
            margin: 0;
        }
        dl {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px;
        }
        dt {
            font-weight: bold;
            color: #555;
        }
        dd {
            color: #333;
        }
        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .overlay.active {
            display: flex;
        }
        .overlay img {
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }
        .close-overlay {
            position: absolute;
            top: 20px;
            right: 30px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            border: none;
            font-size: 36px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            line-height: 1;
            padding: 0;
        }
        .close-overlay:hover {
            background: white;
            transform: scale(1.1);
        }
        .nav-overlay {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.8);
            color: #333;
            border: none;
            font-size: 32px;
            width: 50px;
            height: 50px;
            border-radius: 4px;
            cursor: pointer;
            user-select: none;
            display: none;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            line-height: 1;
            padding: 0;
        }
        #prev-btn {
            left: 20px;
        }
        #next-btn {
            right: 20px;
        }
        .nav-overlay:hover {
            background: white;
            transform: translateY(-50%) scale(1.1);
        }
        .overlay-counter {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{FILENAME}}</h1>
            <div class="diff-percentage">{{PERCENT_DIFF}}% Different</div>
            <div class="breadcrumb">
                <a href="summary.html">Summary</a>
                <span class="breadcrumb-separator">›</span>
                {{BREADCRUMB_MIDDLE}}
                <span class="breadcrumb-separator">›</span>
                <span>{{FILENAME}}</span>
            </div>
        </header>

        <div class="nav-buttons">
            <div class="nav-left">
                <a href="{{SUBDIR_LINK}}" class="btn btn-back">← Back to Directory</a>
            </div>
            <div class="nav-right">
                {{PREV_LINK}}
                {{NEXT_LINK}}
            </div>
        </div>
        
        <div class="image-grid">
            <div class="image-card">
                <h2>Known Good</h2>
                <img src="{{KNOWN_GOOD_IMAGE}}" alt="Known Good" onclick="showOverlay(this.src)">
            </div>
            
            <div class="image-card">
                <h2>New Image</h2>
                <img src="{{NEW_IMAGE}}" alt="New" onclick="showOverlay(this.src)">
            </div>
            
            <div class="image-card">
                <h2>Difference (Enhanced)</h2>
                <img src="{{DIFF_IMAGE}}" alt="Diff" onclick="showOverlay(this.src)">
            </div>
            
            <div class="image-card">
                <h2>Annotated Differences</h2>
                <img src="{{ANNOTATED_IMAGE}}" alt="Annotated" onclick="showOverlay(this.src)">
            </div>
        </div>

        {{HISTORICAL_SECTION}}

        {{FLIP_SECTION}}

        {{HISTOGRAM_SECTION}}

        <div class="metrics">
            <h2>Detailed Metrics</h2>
            {{METRICS}}
        </div>
    </div>
    
    <div class="overlay" id="overlay" onclick="hideOverlay()">
        <button class="close-overlay" onclick="hideOverlay(); event.stopPropagation();">×</button>
        <button class="nav-overlay" id="prev-btn" onclick="previousImage(); event.stopPropagation();">‹</button>
        <button class="nav-overlay" id="next-btn" onclick="nextImage(); event.stopPropagation();">›</button>
        <img id="overlay-img" src="" alt="Full size">
        <div id="overlay-counter" class="overlay-counter"></div>
    </div>
    
    <script>
        // Image navigation state
        let overlayImages = [
            '{{KNOWN_GOOD_IMAGE}}',
            '{{NEW_IMAGE}}',
            '{{DIFF_IMAGE}}',
            '{{ANNOTATED_IMAGE}}'
        ];
        let overlayLabels = ['Known Good', 'New', 'Diff', 'Annotated'];
        let currentImageIndex = 0;
        
        function showOverlay(src) {
            // Find the index of the clicked image
            currentImageIndex = overlayImages.indexOf(src);
            if (currentImageIndex === -1) {
                currentImageIndex = 0;
            }
            updateOverlayImage();
            document.getElementById('overlay').classList.add('active');
            updateNavigationButtons();
        }
        
        function updateOverlayImage() {
            const overlayImg = document.getElementById('overlay-img');
            const counterDiv = document.getElementById('overlay-counter');
            
            overlayImg.src = overlayImages[currentImageIndex];
            counterDiv.textContent = overlayLabels[currentImageIndex] + ' (' + (currentImageIndex + 1) + '/4)';
        }
        
        function updateNavigationButtons() {
            const prevBtn = document.getElementById('prev-btn');
            const nextBtn = document.getElementById('next-btn');
            
            // Show/hide prev button
            prevBtn.style.display = currentImageIndex > 0 ? 'block' : 'none';
            // Show/hide next button
            nextBtn.style.display = currentImageIndex < overlayImages.length - 1 ? 'block' : 'none';
        }
        
        function previousImage() {
            if (currentImageIndex > 0) {
                currentImageIndex--;
                updateOverlayImage();
                updateNavigationButtons();
            }
        }
        
        function nextImage() {
            if (currentImageIndex < overlayImages.length - 1) {
                currentImageIndex++;
                updateOverlayImage();
                updateNavigationButtons();
            }
        }
        
        function hideOverlay() {
            document.getElementById('overlay').classList.remove('active');
        }
        
        function toggleDescription(groupId) {
            const descElement = document.getElementById(groupId + '-desc');
            if (descElement) {
                if (descElement.style.display === 'none') {
                    descElement.style.display = 'block';
                } else {
                    descElement.style.display = 'none';
                }
            }
        }
        
        document.addEventListener('keydown', function(e) {
            const overlay = document.getElementById('overlay');
            if (overlay.classList.contains('active')) {
                if (e.key === 'Escape') hideOverlay();
                if (e.key === 'ArrowLeft') previousImage();
                if (e.key === 'ArrowRight') nextImage();
            }
        });
    </script>
</body>
</html>"""

    def _get_summary_template(self) -> str:
        """Return HTML template for summary page."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Comparison Summary</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .summary-info {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .status-identical { background: #d4edda; }
        .status-minor { background: #fff3cd; }
        .status-moderate { background: #ffe5d0; }
        .status-major { background: #f8d7da; }
        .btn-view {
            background: #3498db;
            color: white;
            padding: 6px 12px;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .btn-view:hover {
            background: #2980b9;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .anomaly-count {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.9em;
        }
        /* Configuration Section Styles */
        .config-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .config-section h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .config-group {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 15px;
        }
        .config-group h3 {
            color: #3498db;
            font-size: 1.1em;
            margin-bottom: 10px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        .config-list {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 8px 15px;
        }
        .config-list dt {
            font-weight: 600;
            color: #555;
        }
        .config-list dd {
            color: #333;
        }
        .config-list code {
            background: #f1f3f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Comparison Summary</h1>
        <div class="summary-info">
            Total comparisons: <strong>{{TOTAL_COUNT}}</strong><br>
            Results grouped by subdirectory
        </div>

        {{CONFIG_SECTION}}

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Directory</th>
                    <th>Images</th>
                    <th>Avg Diff %</th>
                    <th>Max Diff %</th>
                    <th>Avg Composite</th>
                    <th>Anomalies</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {{ROWS}}
            </tbody>
        </table>
    </div>
</body>
</html>"""
