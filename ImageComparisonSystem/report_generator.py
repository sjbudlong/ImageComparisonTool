"""
HTML report generation for image comparison results.

Provides functionality to generate detailed HTML reports for individual
image comparisons and summary pages showing all results.
"""

import logging
from pathlib import Path
from typing import List, Optional
from config import Config
from models import ComparisonResult

logger = logging.getLogger("ImageComparison")


class ReportGenerator:
    """Generates HTML reports for comparison results.
    
    Creates detailed HTML reports for each image comparison and a summary
    page with navigation and statistics.
    """
    
    # Metric descriptions for tooltips
    METRIC_DESCRIPTIONS = {
        'Pixel Difference': (
            'Compares pixel-by-pixel differences between images. '
            'Shows the percentage of pixels that differ and average RGB distance.'
        ),
        'Structural Similarity': (
            'Measures structural similarity (SSIM) between images on a scale of 0-1. '
            'Higher values indicate more similar images. '
            'Accounts for luminance, contrast, and structure.'
        ),
        'Histogram Analysis': (
            'Analyzes the distribution of color and brightness values. '
            'Compares histograms for each color channel (RGB). '
            'Useful for detecting lighting or contrast changes.'
        ),
    }
    
    def __init__(self, config: Config) -> None:
        """Initialize report generator.
        
        Args:
            config: Configuration object with output paths
        """
        self.config: Config = config
    
    def generate_detail_report(self, result: ComparisonResult, 
                              results: Optional[List[ComparisonResult]] = None) -> None:
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
                safe_subdir = subdir.replace('/', '_').replace('\\', '_')
                subdir_link = f"subdir_{safe_subdir}.html"
                breadcrumb_middle = f'<a href="{subdir_link}">{subdir}</a>'
            else:
                subdir_link = "subdir_root.html"
                breadcrumb_middle = '<a href="subdir_root.html">Ungrouped</a>'

            # Generate navigation links
            prev_link: str = ''
            next_link: str = ''
            if results and len(results) > 1:
                # Find current result index
                try:
                    current_idx: int = next(i for i, r in enumerate(results) if r.filename == result.filename)

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

            html: str = self._get_html_template()
            html = html.replace('{{TITLE}}', f"Comparison: {result.filename}")
            html = html.replace('{{FILENAME}}', result.filename)
            html = html.replace('{{PERCENT_DIFF}}', f"{result.percent_different:.4f}")
            html = html.replace('{{NEW_IMAGE}}', new_img_rel)
            html = html.replace('{{KNOWN_GOOD_IMAGE}}', known_good_rel)
            html = html.replace('{{DIFF_IMAGE}}', diff_rel)
            html = html.replace('{{ANNOTATED_IMAGE}}', annotated_rel)
            html = html.replace('{{METRICS}}', self._format_metrics(result.metrics))
            html = html.replace('{{HISTOGRAM_DATA}}', result.histogram_data or '')
            html = html.replace('{{BREADCRUMB_MIDDLE}}', breadcrumb_middle)
            html = html.replace('{{SUBDIR_LINK}}', subdir_link)
            html = html.replace('{{PREV_LINK}}', prev_link)
            html = html.replace('{{NEXT_LINK}}', next_link)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Generated report: {output_path.name}")
        except Exception as e:
            logger.error(f"Error generating report for {result.filename}: {e}", exc_info=True)
    
    def generate_summary_report(self, results: List[ComparisonResult]):
        """Generate summary HTML report listing all comparisons grouped by subdirectory."""
        output_path = self.config.html_path / 'summary.html'

        try:
            # Group results by subdirectory
            grouped = self._group_by_subdirectory(results)

            # Sort subdirectories: empty string (root) first, then alphabetically
            sorted_subdirs = sorted(grouped.keys(), key=lambda x: (x != '', x))

            rows_html = []
            for idx, subdir in enumerate(sorted_subdirs):
                subdir_results = grouped[subdir]

                # Calculate statistics
                image_count = len(subdir_results)
                avg_diff = sum(r.percent_different for r in subdir_results) / image_count
                max_diff = max(r.percent_different for r in subdir_results)

                # Determine status class based on max difference
                status_class = self._get_status_class(max_diff)

                # Display name and link
                if subdir:
                    display_name = subdir
                    safe_subdir = subdir.replace('/', '_').replace('\\', '_')
                    subdir_link = f"subdir_{safe_subdir}.html"
                else:
                    display_name = "Ungrouped"
                    subdir_link = "subdir_root.html"

                row = f'''
                <tr class="{status_class}">
                    <td>{idx + 1}</td>
                    <td><a href="{subdir_link}">{display_name}</a></td>
                    <td>{image_count}</td>
                    <td>{avg_diff:.4f}%</td>
                    <td>{max_diff:.4f}%</td>
                    <td>
                        <a href="{subdir_link}" class="btn-view">View Directory</a>
                    </td>
                </tr>
            '''
                rows_html.append(row)

            summary_html = self._get_summary_template()
            summary_html = summary_html.replace('{{TOTAL_COUNT}}', str(len(results)))
            summary_html = summary_html.replace('{{ROWS}}', '\n'.join(rows_html))

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_html)
            logger.info("Generated summary report: summary.html")
        except Exception as e:
            logger.error(f"Error generating summary report: {e}", exc_info=True)

    def generate_subdirectory_index(self, subdirectory: str, results: List[ComparisonResult]) -> None:
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
            safe_subdir = subdirectory.replace('/', '_').replace('\\', '_')
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

                # Build card HTML
                card = f'''
            <a href="{detail_link}" class="comparison-card {status_class}">
                <div class="card-header">
                    <div class="filename">{result.filename}</div>
                    <div class="diff-badge">{result.percent_different:.4f}% diff</div>
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
            '''
                cards_html.append(card)

            # Get template and replace placeholders
            html = self._get_subdirectory_index_template()
            html = html.replace('{{SUBDIRECTORY}}', display_name)
            html = html.replace('{{SUBDIRECTORY_DISPLAY}}', display_name)
            html = html.replace('{{BACK_TO_SUMMARY}}', 'summary.html')
            html = html.replace('{{IMAGE_COUNT}}', str(len(results)))
            html = html.replace('{{PLURAL}}', 's' if len(results) != 1 else '')
            html = html.replace('{{COMPARISON_CARDS}}', '\n'.join(cards_html))

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"Generated subdirectory index: {output_filename}")

        except Exception as e:
            logger.error(f"Error generating subdirectory index for {subdirectory}: {e}", exc_info=True)

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
            return rel.replace('\\', '/')
        except Exception:
            return str(path)
    
    def _format_metrics(self, metrics: dict) -> str:
        """Format metrics dictionary as HTML with togglable descriptions."""
        html_parts = []
        
        for analyzer_name, analyzer_metrics in metrics.items():
            # Generate unique ID for this metric group
            group_id = analyzer_name.lower().replace(' ', '-')
            description = self.METRIC_DESCRIPTIONS.get(analyzer_name, '')
            
            html_parts.append(f'<div class="metric-group">')
            html_parts.append(f'<div class="metric-header" onclick="toggleDescription(\'{group_id}\')">')
            html_parts.append(f'<h3>{analyzer_name}</h3>')
            if description:
                html_parts.append(f'<span class="metric-help-icon" title="Click to see description">?</span>')
            html_parts.append('</div>')
            
            if description:
                html_parts.append(f'<div class="metric-description" id="{group_id}-desc" style="display: none;">')
                html_parts.append(f'<p>{description}</p>')
                html_parts.append('</div>')
            
            html_parts.append('<dl>')
            
            for key, value in analyzer_metrics.items():
                if key != 'error':
                    formatted_value = self._format_value(value)
                    html_parts.append(f'<dt>{self._format_key(key)}</dt>')
                    html_parts.append(f'<dd>{formatted_value}</dd>')
            
            html_parts.append('</dl>')
            html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _format_key(self, key: str) -> str:
        """Format metric key for display."""
        return key.replace('_', ' ').title()
    
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
            return 'status-identical'
        elif percent_diff < 1.0:
            return 'status-minor'
        elif percent_diff < 5.0:
            return 'status-moderate'
        else:
            return 'status-major'
    
    def _get_status_text(self, percent_diff: float) -> str:
        """Get status text based on difference percentage."""
        if percent_diff < 0.1:
            return 'Nearly Identical'
        elif percent_diff < 1.0:
            return 'Minor Differences'
        elif percent_diff < 5.0:
            return 'Moderate Differences'
        else:
            return 'Major Differences'
    
    def _get_nav_link(self, direction: str, result: ComparisonResult) -> str:
        """Generate navigation link HTML - deprecated, kept for compatibility."""
        # Navigation is now handled in generate_detail_report
        return ''

    def _get_subdirectory_index_template(self) -> str:
        """Return HTML template for subdirectory index page.

        Creates a template showing all images in a subdirectory with thumbnails.
        Each entry displays 4 thumbnails in a horizontal row: new, known_good,
        diff, and annotated_diff images.
        """
        return '''<!DOCTYPE html>
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
        }
        .diff-badge {
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
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
</html>'''

    def _get_html_template(self) -> str:
        """Return HTML template for detail page."""
        return '''<!DOCTYPE html>
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
        
        <div class="metrics">
            <h2>Histogram Comparison</h2>
            <img src="data:image/png;base64,{{HISTOGRAM_DATA}}" alt="Histograms" style="width: 100%; max-width: 1000px; margin: 20px 0;">
        </div>
        
        <div class="metrics">
            <h2>Detailed Metrics</h2>
            {{METRICS}}
        </div>
    </div>
    
    <div class="overlay" id="overlay" onclick="hideOverlay()">
        <button class="close-overlay" onclick="hideOverlay(); event.stopPropagation();">×</button>
        <img id="overlay-img" src="" alt="Full size">
    </div>
    
    <script>
        function showOverlay(src) {
            document.getElementById('overlay-img').src = src;
            document.getElementById('overlay').classList.add('active');
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
            if (e.key === 'Escape') hideOverlay();
        });
    </script>
</body>
</html>'''
    
    def _get_summary_template(self) -> str:
        """Return HTML template for summary page."""
        return '''<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Comparison Summary</h1>
        <div class="summary-info">
            Total comparisons: <strong>{{TOTAL_COUNT}}</strong><br>
            Results grouped by subdirectory
        </div>

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Directory</th>
                    <th>Images</th>
                    <th>Avg Diff %</th>
                    <th>Max Diff %</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {{ROWS}}
            </tbody>
        </table>
    </div>
</body>
</html>'''
