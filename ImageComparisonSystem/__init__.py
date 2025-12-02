"""
Image Comparison System - Advanced image comparison and analysis tool.

A modular Python system for comparing images and generating detailed HTML reports
with visual diffs. Perfect for 3D rendering validation, visual regression testing,
and quality assurance workflows.

Version: 1.0.0
License: MIT
Repository: https://github.com/sjbudlong/ImageComparisonTool
"""

__version__ = "1.0.0"
__author__ = "sjbudlong"
__license__ = "MIT"

from .config import Config
from .models import ComparisonResult
from .comparator import ImageComparator
from .processor import ImageProcessor
from .report_generator import ReportGenerator
from .markdown_exporter import MarkdownExporter

__all__ = [
    "Config",
    "ComparisonResult",
    "ImageComparator",
    "ImageProcessor",
    "ReportGenerator",
    "MarkdownExporter",
    "__version__",
]
