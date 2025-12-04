"""
Annotation management module for ML training data.

Provides CRUD operations for managing annotations on image comparison results,
supporting various geometry types (bounding boxes, polygons, points, classifications).
"""

from .annotation_manager import AnnotationManager
from .export_formats import COCOExporter, YOLOExporter, ExportManager

__all__ = ["AnnotationManager", "COCOExporter", "YOLOExporter", "ExportManager"]
