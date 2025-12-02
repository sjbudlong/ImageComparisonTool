"""
Markdown export functionality for image comparison results.

Provides markdown report generation suitable for CI/CD pipelines,
particularly Azure DevOps, GitHub Actions, and build notifications.
"""

import logging
from pathlib import Path
from typing import List
from datetime import datetime

# Handle both package and direct module imports
try:
    from .models import ComparisonResult
except ImportError:
    from models import ComparisonResult  # type: ignore

logger = logging.getLogger("ImageComparison")


class MarkdownExporter:
    """Exports comparison results to markdown format for CI/CD integration."""
    
    def __init__(self, output_dir: Path) -> None:
        """Initialize markdown exporter.
        
        Args:
            output_dir: Directory where markdown reports will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_summary(self, results: List[ComparisonResult], base_path: Path = None) -> Path:
        """Generate markdown summary report for CI/CD pipeline integration.
        
        Creates a markdown file suitable for:
        - Azure DevOps Pipeline summaries
        - GitHub Actions workflow summaries
        - Build reports and notifications
        - Email attachments
        
        The markdown format is pipeline-agnostic and parseable by various tools.
        Detailed results are grouped by subdirectory structure.
        
        Args:
            results: List of comparison results
            base_path: Optional base path for extracting subdirectories
            
        Returns:
            Path to generated markdown file
        """
        output_path = self.output_dir / 'summary.md'
        
        try:
            # Calculate statistics
            total = len(results)
            identical = sum(1 for r in results if r.percent_different < 0.1)
            minor = sum(1 for r in results if 0.1 <= r.percent_different < 1.0)
            moderate = sum(1 for r in results if 1.0 <= r.percent_different < 5.0)
            major = sum(1 for r in results if r.percent_different >= 5.0)
            
            max_diff = max(r.percent_different for r in results) if results else 0
            min_diff = min(r.percent_different for r in results) if results else 0
            avg_diff = sum(r.percent_different for r in results) / total if total > 0 else 0
            
            # Build markdown content
            md_lines = [
                "# Image Comparison Summary",
                "",
                "## Statistics",
                "",
                f"- **Total Comparisons**: {total}",
                f"- **Nearly Identical** (<0.1%): {identical}",
                f"- **Minor Differences** (0.1-1%): {minor}",
                f"- **Moderate Differences** (1-5%): {moderate}",
                f"- **Major Differences** (≥5%): {major}",
                "",
            ]
            
            # Add statistics table
            md_lines.extend([
                "## Difference Statistics",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Maximum Difference | {max_diff:.4f}% |",
                f"| Minimum Difference | {min_diff:.4f}% |",
                f"| Average Difference | {avg_diff:.4f}% |",
                "",
            ])
            
            # Determine overall status
            overall_status = self._get_overall_status(results)
            status_emoji = self._get_status_emoji(overall_status)
            md_lines.extend([
                "## Overall Status",
                "",
                f"{status_emoji} **{overall_status}**",
                "",
            ])
            
            # Add results grouped by subdirectory
            md_lines.extend([
                "## Detailed Results",
                "",
            ])
            
            # Group results by subdirectory
            grouped_results = self._group_results_by_subdirectory(results, base_path)
            
            # Add results for each subdirectory
            for subdir, subdir_results in grouped_results:
                # Add subdirectory header
                if subdir:
                    md_lines.append(f"### {subdir}")
                else:
                    md_lines.append("### Root Directory")
                md_lines.append("")
                
                # Add results table for this subdirectory
                md_lines.extend([
                    "| # | Filename | Difference % | Status | Details |",
                    "|---|----------|-------------|--------|---------|",
                ])
                
                for idx, result in enumerate(subdir_results, 1):
                    status = self._get_status_text(result.percent_different)
                    status_emoji = self._get_status_emoji(status)
                    detail_link = f"[View →]({result.filename}.html)"
                    md_lines.append(
                        f"| {idx} | `{result.filename}` | {result.percent_different:.4f}% | {status_emoji} {status} | {detail_link} |"
                    )
                
                md_lines.append("")
            
            # Add footer with links and metadata
            md_lines.extend([
                "",
                "---",
                "",
                "## Reports",
                "",
                "- [HTML Summary Report](summary.html) - Interactive dashboard with images",
                "- [Results JSON](results.json) - Machine-readable format",
                "",
                f"*Generated: {self._get_timestamp()}*",
            ])
            
            markdown_content = '\n'.join(md_lines)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Generated markdown summary: {output_path.name}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating markdown summary: {e}", exc_info=True)
            raise
    
    def _group_results_by_subdirectory(self, results: List[ComparisonResult], base_path: Path = None) -> List[tuple]:
        """Group comparison results by their subdirectory structure.
        
        Args:
            results: List of comparison results
            base_path: Optional base path for extracting subdirectories
            
        Returns:
            List of tuples (subdirectory, results_in_subdir) sorted by subdirectory name
        """
        from collections import defaultdict
        
        grouped = defaultdict(list)
        
        for result in results:
            if base_path:
                subdir = result.get_subdirectory(base_path)
            else:
                # Try to extract subdirectory from filename path if available
                subdir = ''
                if hasattr(result, 'subdirectory'):
                    subdir = result.subdirectory
            
            grouped[subdir].append(result)
        
        # Sort by subdirectory name, with root directory first
        sorted_groups = sorted(grouped.items(), key=lambda x: (x[0] != '', x[0]))
        
        return sorted_groups
    
    @staticmethod
    def _get_status_text(percent_diff: float) -> str:
        """Get status text based on difference percentage."""
        if percent_diff < 0.1:
            return 'Nearly Identical'
        elif percent_diff < 1.0:
            return 'Minor Differences'
        elif percent_diff < 5.0:
            return 'Moderate Differences'
        else:
            return 'Major Differences'
    
    @staticmethod
    def _get_status_emoji(status: str) -> str:
        """Get emoji for status for pipeline visibility."""
        status_map = {
            'Nearly Identical': '✅',
            'Minor Differences': '⚠️',
            'Moderate Differences': '⚠️',
            'Major Differences': '❌',
        }
        return status_map.get(status, '❓')
    
    @staticmethod
    def _get_overall_status(results: List[ComparisonResult]) -> str:
        """Determine overall comparison status."""
        if not results:
            return 'No comparisons'
        
        major_count = sum(1 for r in results if r.percent_different >= 5.0)
        
        if major_count == 0:
            return 'All comparisons passed'
        elif major_count <= len(results) * 0.1:
            return f'Minor issues detected ({major_count} major difference{"s" if major_count != 1 else ""})'
        else:
            return f'Significant issues detected ({major_count}/{len(results)} images)'
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat(timespec='minutes')
