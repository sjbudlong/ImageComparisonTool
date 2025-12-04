"""
Annotation export formats for ML training.

Provides exporters for COCO and YOLO annotation formats, enabling
annotations to be used for training machine learning models.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Database and AnnotationManager
try:
    from ..history.database import Database
    from .annotation_manager import AnnotationManager
except ImportError:
    try:
        from history.database import Database  # type: ignore
        from annotation_manager import AnnotationManager  # type: ignore
    except ImportError:
        from ImageComparisonSystem.history.database import Database  # type: ignore
        from ImageComparisonSystem.annotations.annotation_manager import AnnotationManager  # type: ignore


class COCOExporter:
    """
    Export annotations in COCO (Common Objects in Context) format.

    COCO format is the industry-standard format for object detection and
    instance segmentation tasks. It includes full metadata, categories,
    and supports multiple annotation types.

    COCO JSON Structure:
        {
            "info": {...},
            "images": [...],
            "annotations": [...],
            "categories": [...]
        }
    """

    def __init__(self, annotation_manager: AnnotationManager, base_dir: Path):
        """
        Initialize COCO exporter.

        Args:
            annotation_manager: AnnotationManager instance
            base_dir: Base directory for image paths

        Example:
            >>> manager = AnnotationManager(db)
            >>> exporter = COCOExporter(manager, Path("./renders"))
            >>> exporter.export_run(run_id=123, output_path="annotations.json")
        """
        self.annotation_manager = annotation_manager
        self.base_dir = base_dir
        logger.debug("COCOExporter initialized")

    def export_run(
        self,
        run_id: int,
        output_path: Path,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Export annotations for a run in COCO format.

        Args:
            run_id: Run ID to export annotations for
            output_path: Path to output JSON file
            include_metadata: Include COCO info section

        Returns:
            Dictionary with export statistics

        Example:
            >>> stats = exporter.export_run(run_id=123, output_path=Path("coco.json"))
            >>> print(f"Exported {stats['annotation_count']} annotations")
        """
        logger.info(f"Exporting annotations for run {run_id} to COCO format")

        # Get annotations for run
        annotations = self.annotation_manager.get_annotations_for_run(run_id)

        if not annotations:
            logger.warning(f"No annotations found for run {run_id}")
            return {
                "success": False,
                "annotation_count": 0,
                "image_count": 0,
                "category_count": 0,
                "output_path": str(output_path)
            }

        # Build COCO structure
        coco_data = {
            "info": self._build_info() if include_metadata else {},
            "images": [],
            "annotations": [],
            "categories": []
        }

        # Build categories from unique labels
        categories = self._build_categories(annotations)
        coco_data["categories"] = categories
        category_map = {cat["name"]: cat["id"] for cat in categories}

        # Build images and annotations
        image_map = {}  # filename -> image_id
        image_id_counter = 1
        annotation_id_counter = 1

        for ann in annotations:
            # Add image if not already added
            filename = ann["filename"]
            if filename not in image_map:
                image_id = image_id_counter
                image_map[filename] = image_id
                image_id_counter += 1

                coco_data["images"].append({
                    "id": image_id,
                    "file_name": filename,
                    "width": 0,  # Unknown - would need to read image
                    "height": 0,  # Unknown - would need to read image
                })

            # Convert annotation to COCO format
            image_id = image_map[filename]
            coco_annotation = self._convert_to_coco_annotation(
                ann,
                annotation_id_counter,
                image_id,
                category_map
            )

            if coco_annotation:
                coco_data["annotations"].append(coco_annotation)
                annotation_id_counter += 1

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(coco_data, f, indent=2)

        logger.info(
            f"COCO export complete: {len(coco_data['annotations'])} annotations, "
            f"{len(coco_data['images'])} images, {len(coco_data['categories'])} categories"
        )

        return {
            "success": True,
            "annotation_count": len(coco_data["annotations"]),
            "image_count": len(coco_data["images"]),
            "category_count": len(coco_data["categories"]),
            "output_path": str(output_path)
        }

    def _build_info(self) -> Dict[str, Any]:
        """Build COCO info section."""
        return {
            "description": "Image Comparison Tool Annotations",
            "version": "1.0",
            "year": datetime.now().year,
            "contributor": "ImageComparisonTool",
            "date_created": datetime.now().isoformat()
        }

    def _build_categories(self, annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build category list from unique labels."""
        unique_labels = set()
        for ann in annotations:
            if ann.get("label"):
                unique_labels.add(ann["label"])

        categories = []
        for idx, label in enumerate(sorted(unique_labels), start=1):
            categories.append({
                "id": idx,
                "name": label,
                "supercategory": "difference"
            })

        return categories

    def _convert_to_coco_annotation(
        self,
        ann: Dict[str, Any],
        annotation_id: int,
        image_id: int,
        category_map: Dict[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Convert internal annotation to COCO format."""
        annotation_type = ann["annotation_type"]
        geometry = ann.get("geometry")

        # Get category ID
        category_id = category_map.get(ann.get("label", "unknown"), 1)

        coco_ann = {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "iscrowd": 0
        }

        # Convert geometry based on type
        if annotation_type == "bounding_box" and geometry:
            # COCO bbox format: [x, y, width, height]
            coco_ann["bbox"] = [
                geometry["x"],
                geometry["y"],
                geometry["width"],
                geometry["height"]
            ]
            coco_ann["area"] = geometry["width"] * geometry["height"]

        elif annotation_type == "polygon" and geometry:
            # COCO segmentation format: [[x1, y1, x2, y2, ...]]
            points = geometry.get("points", [])
            segmentation = []
            for point in points:
                segmentation.extend([point["x"], point["y"]])
            coco_ann["segmentation"] = [segmentation]

            # Calculate bounding box from polygon
            x_coords = [p["x"] for p in points]
            y_coords = [p["y"] for p in points]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            coco_ann["bbox"] = [x_min, y_min, x_max - x_min, y_max - y_min]
            coco_ann["area"] = (x_max - x_min) * (y_max - y_min)

        elif annotation_type == "point" and geometry:
            # COCO doesn't have native point type, use tiny bbox
            coco_ann["bbox"] = [geometry["x"], geometry["y"], 1, 1]
            coco_ann["area"] = 1

        elif annotation_type == "classification":
            # Image-level classification - no bbox
            coco_ann["bbox"] = [0, 0, 0, 0]
            coco_ann["area"] = 0

        else:
            logger.warning(f"Unsupported annotation type: {annotation_type}")
            return None

        return coco_ann


class YOLOExporter:
    """
    Export annotations in YOLO format.

    YOLO format uses normalized coordinates with one text file per image.
    Each line represents one annotation:
        <class_id> <x_center> <y_center> <width> <height>

    All coordinates are normalized to [0, 1] range.
    """

    def __init__(self, annotation_manager: AnnotationManager, base_dir: Path):
        """
        Initialize YOLO exporter.

        Args:
            annotation_manager: AnnotationManager instance
            base_dir: Base directory for image paths

        Example:
            >>> manager = AnnotationManager(db)
            >>> exporter = YOLOExporter(manager, Path("./renders"))
            >>> exporter.export_run(run_id=123, output_dir=Path("./yolo_labels"))
        """
        self.annotation_manager = annotation_manager
        self.base_dir = base_dir
        logger.debug("YOLOExporter initialized")

    def export_run(
        self,
        run_id: int,
        output_dir: Path,
        image_width: int = 1920,
        image_height: int = 1080,
        generate_classes_file: bool = True
    ) -> Dict[str, Any]:
        """
        Export annotations for a run in YOLO format.

        Args:
            run_id: Run ID to export annotations for
            output_dir: Directory to write label files
            image_width: Image width for normalization (default: 1920)
            image_height: Image height for normalization (default: 1080)
            generate_classes_file: Generate classes.txt file

        Returns:
            Dictionary with export statistics

        Example:
            >>> stats = exporter.export_run(run_id=123, output_dir=Path("./labels"))
            >>> print(f"Exported {stats['file_count']} label files")
        """
        logger.info(f"Exporting annotations for run {run_id} to YOLO format")

        # Get annotations for run
        annotations = self.annotation_manager.get_annotations_for_run(run_id)

        if not annotations:
            logger.warning(f"No annotations found for run {run_id}")
            return {
                "success": False,
                "file_count": 0,
                "annotation_count": 0,
                "class_count": 0,
                "output_dir": str(output_dir)
            }

        # Build class mapping
        unique_labels = sorted(set(ann.get("label", "unknown") for ann in annotations if ann.get("label")))
        class_map = {label: idx for idx, label in enumerate(unique_labels)}

        # Group annotations by filename
        annotations_by_file = {}
        for ann in annotations:
            filename = ann["filename"]
            if filename not in annotations_by_file:
                annotations_by_file[filename] = []
            annotations_by_file[filename].append(ann)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write label files
        file_count = 0
        total_annotations = 0

        for filename, file_annotations in annotations_by_file.items():
            # Generate label file path (replace image extension with .txt)
            label_filename = Path(filename).stem + ".txt"
            label_path = output_dir / label_filename

            # Convert annotations to YOLO format
            yolo_lines = []
            for ann in file_annotations:
                yolo_line = self._convert_to_yolo_annotation(
                    ann,
                    class_map,
                    image_width,
                    image_height
                )
                if yolo_line:
                    yolo_lines.append(yolo_line)
                    total_annotations += 1

            # Write label file
            if yolo_lines:
                with open(label_path, 'w') as f:
                    f.write('\n'.join(yolo_lines))
                file_count += 1

        # Write classes.txt file
        if generate_classes_file:
            classes_path = output_dir / "classes.txt"
            with open(classes_path, 'w') as f:
                f.write('\n'.join(unique_labels))
            logger.debug(f"Generated classes.txt with {len(unique_labels)} classes")

        logger.info(
            f"YOLO export complete: {total_annotations} annotations "
            f"in {file_count} files, {len(unique_labels)} classes"
        )

        return {
            "success": True,
            "file_count": file_count,
            "annotation_count": total_annotations,
            "class_count": len(unique_labels),
            "output_dir": str(output_dir)
        }

    def _convert_to_yolo_annotation(
        self,
        ann: Dict[str, Any],
        class_map: Dict[str, int],
        image_width: int,
        image_height: int
    ) -> Optional[str]:
        """
        Convert internal annotation to YOLO format.

        YOLO format: <class_id> <x_center> <y_center> <width> <height>
        All coordinates normalized to [0, 1]
        """
        annotation_type = ann["annotation_type"]
        geometry = ann.get("geometry")

        # Get class ID
        label = ann.get("label", "unknown")
        class_id = class_map.get(label, 0)

        # Only bounding boxes are supported in YOLO
        if annotation_type == "bounding_box" and geometry:
            x = geometry["x"]
            y = geometry["y"]
            w = geometry["width"]
            h = geometry["height"]

            # Convert to center coordinates
            x_center = x + w / 2
            y_center = y + h / 2

            # Normalize to [0, 1]
            x_center_norm = x_center / image_width
            y_center_norm = y_center / image_height
            width_norm = w / image_width
            height_norm = h / image_height

            # Clamp to [0, 1] range
            x_center_norm = max(0.0, min(1.0, x_center_norm))
            y_center_norm = max(0.0, min(1.0, y_center_norm))
            width_norm = max(0.0, min(1.0, width_norm))
            height_norm = max(0.0, min(1.0, height_norm))

            return f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"

        elif annotation_type == "polygon" and geometry:
            # Convert polygon to bounding box
            points = geometry.get("points", [])
            if not points:
                return None

            x_coords = [p["x"] for p in points]
            y_coords = [p["y"] for p in points]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            w = x_max - x_min
            h = y_max - y_min
            x_center = x_min + w / 2
            y_center = y_min + h / 2

            # Normalize
            x_center_norm = max(0.0, min(1.0, x_center / image_width))
            y_center_norm = max(0.0, min(1.0, y_center / image_height))
            width_norm = max(0.0, min(1.0, w / image_width))
            height_norm = max(0.0, min(1.0, h / image_height))

            return f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"

        else:
            # Point and classification types not supported in YOLO
            logger.debug(f"Annotation type '{annotation_type}' not supported in YOLO format")
            return None


class ExportManager:
    """
    High-level export manager supporting multiple formats.

    Provides unified interface for exporting annotations in different formats.
    """

    def __init__(self, database: Database, base_dir: Path):
        """
        Initialize export manager.

        Args:
            database: Database instance
            base_dir: Base directory for image paths
        """
        self.database = database
        self.base_dir = base_dir
        self.annotation_manager = AnnotationManager(database)
        logger.debug("ExportManager initialized")

    def export(
        self,
        run_id: int,
        format: str,
        output_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Export annotations in specified format.

        Args:
            run_id: Run ID to export
            format: Export format ('coco' or 'yolo')
            output_path: Output file or directory path
            **kwargs: Format-specific options

        Returns:
            Dictionary with export statistics

        Example:
            >>> manager = ExportManager(db, Path("./renders"))
            >>> stats = manager.export(run_id=123, format="coco", output_path=Path("annotations.json"))
        """
        if format.lower() == "coco":
            exporter = COCOExporter(self.annotation_manager, self.base_dir)
            return exporter.export_run(run_id, output_path, **kwargs)

        elif format.lower() == "yolo":
            exporter = YOLOExporter(self.annotation_manager, self.base_dir)
            return exporter.export_run(run_id, output_path, **kwargs)

        else:
            raise ValueError(f"Unsupported export format: {format}. Use 'coco' or 'yolo'.")
