"""
Annotation manager for ML training data.

Provides CRUD operations for managing annotations on image comparison results.
Supports various geometry types: bounding_box, polygon, point, classification.
"""

import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Try to import Database
try:
    from ..history.database import Database
except ImportError:
    try:
        from history.database import Database  # type: ignore
    except ImportError:
        from ImageComparisonSystem.history.database import Database  # type: ignore


class AnnotationManager:
    """
    Manages annotations for image comparison results.

    Provides CRUD operations for creating, reading, updating, and deleting
    annotations. Annotations are stored as JSON in the database and can
    represent various geometry types for ML training.
    """

    # Supported annotation types
    ANNOTATION_TYPES = [
        "bounding_box",  # Rectangular region
        "polygon",  # Multi-point polygon
        "point",  # Single point marker
        "classification",  # Image-level label (no geometry)
    ]

    def __init__(self, database: Database):
        """
        Initialize annotation manager.

        Args:
            database: Database instance for executing queries

        Example:
            >>> db = Database("history.db")
            >>> manager = AnnotationManager(db)
        """
        self.database = database
        logger.debug("AnnotationManager initialized")

    def add_annotation(
        self,
        result_id: int,
        annotation_type: str,
        geometry: Optional[Dict[str, Any]] = None,
        label: Optional[str] = None,
        category: Optional[str] = None,
        confidence: Optional[float] = None,
        annotator_name: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> int:
        """
        Add new annotation to a result.

        Args:
            result_id: Database ID of the result to annotate
            annotation_type: Type of annotation (bounding_box, polygon, point, classification)
            geometry: Geometry data as dictionary (required for non-classification types)
            label: Label or class name (e.g., "rendering_artifact")
            category: Category group (e.g., "rendering_issues", "false_positives")
            confidence: Confidence score 0-1 (optional, for ML predictions)
            annotator_name: Name of person/system creating annotation
            notes: Additional notes or comments

        Returns:
            Annotation ID of newly created annotation

        Raises:
            ValueError: If annotation_type is invalid or geometry is missing

        Example:
            >>> # Bounding box annotation
            >>> geometry = {"x": 100, "y": 200, "width": 150, "height": 100}
            >>> ann_id = manager.add_annotation(
            ...     result_id=123,
            ...     annotation_type="bounding_box",
            ...     geometry=geometry,
            ...     label="lighting_artifact",
            ...     category="rendering_issues",
            ...     annotator_name="john_doe"
            ... )

            >>> # Classification (no geometry)
            >>> ann_id = manager.add_annotation(
            ...     result_id=456,
            ...     annotation_type="classification",
            ...     label="false_positive",
            ...     category="data_issues"
            ... )
        """
        # Validate annotation type
        if annotation_type not in self.ANNOTATION_TYPES:
            raise ValueError(
                f"Invalid annotation_type: {annotation_type}. "
                f"Must be one of: {', '.join(self.ANNOTATION_TYPES)}"
            )

        # Validate geometry requirement
        if annotation_type != "classification" and geometry is None:
            raise ValueError(f"geometry is required for annotation_type '{annotation_type}'")

        # Serialize geometry to JSON
        geometry_json = json.dumps(geometry) if geometry else None

        # Insert annotation
        try:
            annotation_id = self.database.execute_insert(
                """INSERT INTO annotations (
                    result_id, annotation_type, geometry_json, label, category,
                    confidence, annotator_name, notes, annotation_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result_id,
                    annotation_type,
                    geometry_json,
                    label,
                    category,
                    confidence,
                    annotator_name,
                    notes,
                    datetime.now().isoformat(),
                ),
            )

            logger.info(
                f"Created annotation {annotation_id} for result {result_id} "
                f"(type: {annotation_type}, label: {label})"
            )
            return annotation_id

        except Exception as e:
            logger.error(f"Failed to create annotation: {e}")
            raise

    def get_annotation(self, annotation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get annotation by ID.

        Args:
            annotation_id: Annotation ID to retrieve

        Returns:
            Dictionary with annotation data, or None if not found

        Example:
            >>> annotation = manager.get_annotation(123)
            >>> print(annotation["label"])
            'lighting_artifact'
        """
        try:
            rows = self.database.execute_query(
                "SELECT * FROM annotations WHERE annotation_id = ?", (annotation_id,)
            )

            if not rows:
                return None

            annotation = dict(rows[0])

            # Parse geometry JSON
            if annotation["geometry_json"]:
                annotation["geometry"] = json.loads(annotation["geometry_json"])
            else:
                annotation["geometry"] = None

            del annotation["geometry_json"]  # Remove raw JSON field

            return annotation

        except Exception as e:
            logger.error(f"Failed to get annotation {annotation_id}: {e}")
            return None

    def get_annotations_for_result(self, result_id: int) -> List[Dict[str, Any]]:
        """
        Get all annotations for a specific result.

        Args:
            result_id: Result ID to get annotations for

        Returns:
            List of annotation dictionaries

        Example:
            >>> annotations = manager.get_annotations_for_result(123)
            >>> print(f"Found {len(annotations)} annotations")
        """
        try:
            rows = self.database.execute_query(
                "SELECT * FROM annotations WHERE result_id = ? ORDER BY annotation_timestamp DESC",
                (result_id,),
            )

            annotations = []
            for row in rows:
                annotation = dict(row)

                # Parse geometry JSON
                if annotation["geometry_json"]:
                    annotation["geometry"] = json.loads(annotation["geometry_json"])
                else:
                    annotation["geometry"] = None

                del annotation["geometry_json"]
                annotations.append(annotation)

            return annotations

        except Exception as e:
            logger.error(f"Failed to get annotations for result {result_id}: {e}")
            return []

    def get_annotations_for_run(self, run_id: int) -> List[Dict[str, Any]]:
        """
        Get all annotations for results in a specific run.

        Args:
            run_id: Run ID to get annotations for

        Returns:
            List of annotation dictionaries (includes result info)

        Example:
            >>> annotations = manager.get_annotations_for_run(456)
            >>> for ann in annotations:
            ...     print(f"{ann['filename']}: {ann['label']}")
        """
        try:
            rows = self.database.execute_query(
                """SELECT a.*, r.filename, r.subdirectory
                FROM annotations a
                JOIN results r ON a.result_id = r.result_id
                WHERE r.run_id = ?
                ORDER BY a.annotation_timestamp ASC""",
                (run_id,),
            )

            annotations = []
            for row in rows:
                annotation = dict(row)

                # Parse geometry JSON
                if annotation["geometry_json"]:
                    annotation["geometry"] = json.loads(annotation["geometry_json"])
                else:
                    annotation["geometry"] = None

                del annotation["geometry_json"]
                annotations.append(annotation)

            return annotations

        except Exception as e:
            logger.error(f"Failed to get annotations for run {run_id}: {e}")
            return []

    def update_annotation(
        self,
        annotation_id: int,
        geometry: Optional[Dict[str, Any]] = None,
        label: Optional[str] = None,
        category: Optional[str] = None,
        confidence: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Update an existing annotation.

        Args:
            annotation_id: Annotation ID to update
            geometry: New geometry data (optional)
            label: New label (optional)
            category: New category (optional)
            confidence: New confidence score (optional)
            notes: New notes (optional)

        Returns:
            True if update successful, False otherwise

        Example:
            >>> # Update label and confidence
            >>> manager.update_annotation(
            ...     annotation_id=123,
            ...     label="confirmed_artifact",
            ...     confidence=1.0
            ... )
        """
        # Build update query dynamically based on provided fields
        updates = []
        params = []

        if geometry is not None:
            updates.append("geometry_json = ?")
            params.append(json.dumps(geometry))

        if label is not None:
            updates.append("label = ?")
            params.append(label)

        if category is not None:
            updates.append("category = ?")
            params.append(category)

        if confidence is not None:
            updates.append("confidence = ?")
            params.append(confidence)

        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)

        if not updates:
            logger.warning(f"No fields to update for annotation {annotation_id}")
            return False

        # Add annotation_id to params
        params.append(annotation_id)

        query = f"UPDATE annotations SET {', '.join(updates)} WHERE annotation_id = ?"

        try:
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Updated annotation {annotation_id}")
                    return True
                else:
                    logger.warning(f"Annotation {annotation_id} not found")
                    return False

        except Exception as e:
            logger.error(f"Failed to update annotation {annotation_id}: {e}")
            return False

    def delete_annotation(self, annotation_id: int) -> bool:
        """
        Delete an annotation.

        Args:
            annotation_id: Annotation ID to delete

        Returns:
            True if deletion successful, False otherwise

        Example:
            >>> manager.delete_annotation(123)
        """
        try:
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM annotations WHERE annotation_id = ?", (annotation_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Deleted annotation {annotation_id}")
                    return True
                else:
                    logger.warning(f"Annotation {annotation_id} not found")
                    return False

        except Exception as e:
            logger.error(f"Failed to delete annotation {annotation_id}: {e}")
            return False

    def get_annotations_by_label(self, label: str) -> List[Dict[str, Any]]:
        """
        Get all annotations with a specific label.

        Args:
            label: Label to search for

        Returns:
            List of annotation dictionaries

        Example:
            >>> artifacts = manager.get_annotations_by_label("lighting_artifact")
        """
        try:
            rows = self.database.execute_query(
                """SELECT a.*, r.filename, r.subdirectory, r.run_id
                FROM annotations a
                JOIN results r ON a.result_id = r.result_id
                WHERE a.label = ?
                ORDER BY a.annotation_timestamp DESC""",
                (label,),
            )

            annotations = []
            for row in rows:
                annotation = dict(row)

                # Parse geometry JSON
                if annotation["geometry_json"]:
                    annotation["geometry"] = json.loads(annotation["geometry_json"])
                else:
                    annotation["geometry"] = None

                del annotation["geometry_json"]
                annotations.append(annotation)

            return annotations

        except Exception as e:
            logger.error(f"Failed to get annotations by label '{label}': {e}")
            return []

    def get_annotations_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all annotations in a specific category.

        Args:
            category: Category to search for

        Returns:
            List of annotation dictionaries

        Example:
            >>> issues = manager.get_annotations_by_category("rendering_issues")
        """
        try:
            rows = self.database.execute_query(
                """SELECT a.*, r.filename, r.subdirectory, r.run_id
                FROM annotations a
                JOIN results r ON a.result_id = r.result_id
                WHERE a.category = ?
                ORDER BY a.annotation_timestamp DESC""",
                (category,),
            )

            annotations = []
            for row in rows:
                annotation = dict(row)

                # Parse geometry JSON
                if annotation["geometry_json"]:
                    annotation["geometry"] = json.loads(annotation["geometry_json"])
                else:
                    annotation["geometry"] = None

                del annotation["geometry_json"]
                annotations.append(annotation)

            return annotations

        except Exception as e:
            logger.error(f"Failed to get annotations by category '{category}': {e}")
            return []

    def get_annotation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about annotations in the database.

        Returns:
            Dictionary with annotation statistics

        Example:
            >>> stats = manager.get_annotation_statistics()
            >>> print(f"Total annotations: {stats['total_annotations']}")
            >>> print(f"By type: {stats['by_type']}")
        """
        stats = {
            "total_annotations": 0,
            "by_type": {},
            "by_category": {},
            "unique_labels": [],
            "annotators": [],
        }

        try:
            # Total count
            rows = self.database.execute_query("SELECT COUNT(*) as count FROM annotations")
            stats["total_annotations"] = rows[0]["count"] if rows else 0

            # Count by type
            rows = self.database.execute_query(
                """SELECT annotation_type, COUNT(*) as count
                FROM annotations
                GROUP BY annotation_type"""
            )
            stats["by_type"] = {row["annotation_type"]: row["count"] for row in rows}

            # Count by category
            rows = self.database.execute_query(
                """SELECT category, COUNT(*) as count
                FROM annotations
                WHERE category IS NOT NULL
                GROUP BY category"""
            )
            stats["by_category"] = {row["category"]: row["count"] for row in rows}

            # Unique labels
            rows = self.database.execute_query(
                """SELECT DISTINCT label FROM annotations
                WHERE label IS NOT NULL
                ORDER BY label"""
            )
            stats["unique_labels"] = [row["label"] for row in rows]

            # Annotators
            rows = self.database.execute_query(
                """SELECT DISTINCT annotator_name FROM annotations
                WHERE annotator_name IS NOT NULL
                ORDER BY annotator_name"""
            )
            stats["annotators"] = [row["annotator_name"] for row in rows]

        except Exception as e:
            logger.error(f"Failed to get annotation statistics: {e}")

        return stats

    def validate_geometry(self, annotation_type: str, geometry: Dict[str, Any]) -> bool:
        """
        Validate geometry data for a given annotation type.

        Args:
            annotation_type: Type of annotation
            geometry: Geometry data to validate

        Returns:
            True if valid, False otherwise

        Example:
            >>> geometry = {"x": 10, "y": 20, "width": 100, "height": 50}
            >>> manager.validate_geometry("bounding_box", geometry)
            True
        """
        if annotation_type == "bounding_box":
            required = ["x", "y", "width", "height"]
            return all(key in geometry for key in required)

        elif annotation_type == "polygon":
            # Polygon requires list of points
            if "points" not in geometry:
                return False
            points = geometry["points"]
            if not isinstance(points, list) or len(points) < 3:
                return False
            # Each point should have x, y
            return all(isinstance(p, dict) and "x" in p and "y" in p for p in points)

        elif annotation_type == "point":
            required = ["x", "y"]
            return all(key in geometry for key in required)

        elif annotation_type == "classification":
            # No geometry required
            return True

        return False
