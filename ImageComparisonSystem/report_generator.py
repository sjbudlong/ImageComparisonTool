"""
HTML report generation for image comparison results.
"""

from pathlib import Path
from typing import List
from config import Config
from models import ComparisonResult


class ReportGenerator:
    """Generates HTML reports for comparison results."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def generate_detail_report(self, result: ComparisonResult, results: List[ComparisonResult] = None):
        """Generate detailed HTML report for a single comparison."""
        output_path = self.config.html_path / f"{result.filename}.html"
        
        try:
            # Get relative paths for images
            new_img_rel = self._get_relative_path(result.new_image_path)
            known_good_rel = self._get_relative_path(result.known_good_path)
            diff_rel = self._get_relative_path(result.diff_image_path)
            annotated_rel = self._get_relative_path(result.annotated_image_path)
            
            # Generate navigation links
            prev_link = ''
            next_link = ''
            if results and len(results) > 1:
                # Find current result index
                try:
                    current_idx = next(i for i, r in enumerate(results) if r.filename == result.filename)
                    
                    # Previous link
                    if current_idx > 0:
                        prev_result = results[current_idx - 1]
                        prev_link = f'<a href="{prev_result.filename}.html" class="btn">← Previous</a>'
                    
                    # Next link
                    if current_idx < len(results) - 1:
                        next_result = results[current_idx + 1]
                        next_link = f'<a href="{next_result.filename}.html" class="btn">Next →</a>'
                except StopIteration:
                    pass
            
            html = self._get_html_template()
            html = html.replace('{{TITLE}}', f"Comparison: {result.filename}")
            html = html.replace('{{FILENAME}}', result.filename)
            html = html.replace('{{PERCENT_DIFF}}', f"{result.percent_different:.4f}")
            html = html.replace('{{NEW_IMAGE}}', new_img_rel)
            html = html.replace('{{KNOWN_GOOD_IMAGE}}', known_good_rel)
            html = html.replace('{{DIFF_IMAGE}}', diff_rel)
            html = html.replace('{{ANNOTATED_IMAGE}}', annotated_rel)
            html = html.replace('{{METRICS}}', self._format_metrics(result.metrics))
            html = html.replace('{{HISTOGRAM_DATA}}', result.histogram_data or '')
            html = html.replace('{{PREV_LINK}}', prev_link)
            html = html.replace('{{NEXT_LINK}}', next_link)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"    + Generated report: {output_path.name}")
        except Exception as e:
            print(f"    - Error generating report for {result.filename}: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_summary_report(self, results: List[ComparisonResult]):
        """Generate summary HTML report listing all comparisons."""
        output_path = self.config.html_path / 'summary.html'
        
        try:
            rows_html = []
            for idx, result in enumerate(results):
                detail_link = f"{result.filename}.html"
                status_class = self._get_status_class(result.percent_different)
                
                row = f'''
                <tr class="{status_class}">
                    <td>{idx + 1}</td>
                    <td><a href="{detail_link}">{result.filename}</a></td>
                    <td>{result.percent_different:.4f}%</td>
                    <td>{self._get_status_text(result.percent_different)}</td>
                    <td>
                        <a href="{detail_link}" class="btn-view">View Details</a>
                    </td>
                </tr>
            '''
                rows_html.append(row)
            
            summary_html = self._get_summary_template()
            summary_html = summary_html.replace('{{TOTAL_COUNT}}', str(len(results)))
            summary_html = summary_html.replace('{{ROWS}}', '\n'.join(rows_html))
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_html)
            print(f"  + Generated summary report: summary.html")
        except Exception as e:
            print(f"  - Error generating summary report: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_relative_path(self, path: Path) -> str:
        """Get relative path from HTML directory to image."""
        try:
            return str(path.relative_to(self.config.base_dir))
        except ValueError:
            return str(path)
    
    def _format_metrics(self, metrics: dict) -> str:
        """Format metrics dictionary as HTML."""
        html_parts = []
        
        for analyzer_name, analyzer_metrics in metrics.items():
            html_parts.append(f'<div class="metric-group">')
            html_parts.append(f'<h3>{analyzer_name}</h3>')
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
        .nav-buttons {
            margin: 20px 0;
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
        }
        .btn:hover { background: #2980b9; }
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
        .metric-group h3 {
            color: #2c3e50;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #3498db;
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
        </header>
        
        <div class="nav-buttons">
            <a href="summary.html" class="btn">← Back to Summary</a>
            {{PREV_LINK}}
            {{NEXT_LINK}}
        </div>
        
        <div class="image-grid">
            <div class="image-card">
                <h2>Known Good</h2>
                <img src="../{{KNOWN_GOOD_IMAGE}}" alt="Known Good" onclick="showOverlay(this.src)">
            </div>
            
            <div class="image-card">
                <h2>New Image</h2>
                <img src="../{{NEW_IMAGE}}" alt="New" onclick="showOverlay(this.src)">
            </div>
            
            <div class="image-card">
                <h2>Difference (Enhanced)</h2>
                <img src="../{{DIFF_IMAGE}}" alt="Diff" onclick="showOverlay(this.src)">
            </div>
            
            <div class="image-card">
                <h2>Annotated Differences</h2>
                <img src="../{{ANNOTATED_IMAGE}}" alt="Annotated" onclick="showOverlay(this.src)">
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
            Sorted by difference percentage (highest to lowest)
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Filename</th>
                    <th>Difference %</th>
                    <th>Status</th>
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
