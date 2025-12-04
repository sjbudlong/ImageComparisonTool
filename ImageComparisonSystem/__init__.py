"""
Image Comparison System - Advanced image comparison and analysis tool.

A modular Python system for comparing images and generating detailed HTML
reports with visual diffs. Perfect for 3D rendering validation,
visual regression testing, and quality assurance workflows.

Version: 1.0.0
License: MIT
Repository: https://github.com/sjbudlong/ImageComparisonTool
"""

__version__ = "1.0.0"
__author__ = "sjbudlong"
__license__ = "MIT"

from .config import Config
from .models import ComparisonResult
from .report_generator import ReportGenerator
from .markdown_exporter import MarkdownExporter

# Lazy imports for modules that require optional dependencies
def _get_comparator():
    from .comparator import ImageComparator
    return ImageComparator

def _get_processor():
    from .processor import ImageProcessor
    return ImageProcessor

# Try to import comparator and processor, but don't fail if dependencies missing
try:
    from .comparator import ImageComparator
    from .processor import ImageProcessor
except ImportError:
    # These require skimage - make them lazy imports
    ImageComparator = None
    ImageProcessor = None

__all__ = [
    "Config",
    "ComparisonResult",
    "ImageComparator",
    "ImageProcessor",
    "ReportGenerator",
    "MarkdownExporter",
    "__version__",
]
