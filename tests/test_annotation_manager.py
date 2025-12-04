"""
Unit tests for annotation manager module.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ImageComparisonSystem.history.database import Database
from ImageComparisonSystem.annotations.annotation_manager import AnnotationManager


@pytest.fixture
def temp_database():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        yield db


@pytest.fixture
def populated_database(temp_database):
    """Create a database with test data."""
    db = temp_database

    # Insert test run
    run_id = db.execute_insert(
        """INSERT INTO runs (build_number, timestamp, base_dir, new_dir, known_good_dir,
           config_snapshot, total_images, avg_difference)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ("test-build", datetime.now().isoformat(), "/test", "/test/new", "/test/known", "{}", 10, 5.0),
    )

    # Insert test results
    result_id_1 = db.execute_insert(
        """INSERT INTO results (run_id, filename, subdirectory, new_image_path, known_good_path,
           pixel_difference, ssim_score, composite_score, is_anomaly)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, "test1.png", "", "/test/new/test1.png", "/test/known/test1.png", 10.0, 0.8, 50.0, 0),
    )

    result_id_2 = db.execute_insert(
        """INSERT INTO results (run_id, filename, subdirectory, new_image_path, known_good_path,
           pixel_difference, ssim_score, composite_score, is_anomaly)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, "test2.png", "subdir", "/test/new/subdir/test2.png", "/test/known/subdir/test2.png", 5.0, 0.9, 20.0, 1),
    )

    return db, run_id, [result_id_1, result_id_2]


@pytest.mark.unit
class TestAnnotationManager:
    """Test AnnotationManager class."""

    def test_initialization(self, temp_database):
        """AnnotationManager should initialize with database."""
        manager = AnnotationManager(temp_database)
        assert manager.database is not None
        assert manager.ANNOTATION_TYPES == ["bounding_box", "polygon", "point", "classification"]

    def test_add_bounding_box_annotation(self, populated_database):
        """Should add bounding box annotation successfully."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        geometry = {"x": 100, "y": 200, "width": 150, "height": 100}

        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="bounding_box",
            geometry=geometry,
            label="lighting_artifact",
            category="rendering_issues",
            annotator_name="test_user",
            notes="Test annotation",
        )

        assert ann_id > 0

        # Verify annotation was created
        annotation = manager.get_annotation(ann_id)
        assert annotation is not None
        assert annotation["result_id"] == result_ids[0]
        assert annotation["annotation_type"] == "bounding_box"
        assert annotation["geometry"] == geometry
        assert annotation["label"] == "lighting_artifact"
        assert annotation["category"] == "rendering_issues"
        assert annotation["annotator_name"] == "test_user"

    def test_add_polygon_annotation(self, populated_database):
        """Should add polygon annotation successfully."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        geometry = {
            "points": [
                {"x": 10, "y": 20},
                {"x": 50, "y": 30},
                {"x": 40, "y": 80},
                {"x": 15, "y": 70},
            ]
        }

        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="polygon",
            geometry=geometry,
            label="irregular_artifact",
        )

        assert ann_id > 0

        annotation = manager.get_annotation(ann_id)
        assert annotation["annotation_type"] == "polygon"
        assert annotation["geometry"] == geometry

    def test_add_point_annotation(self, populated_database):
        """Should add point annotation successfully."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        geometry = {"x": 250, "y": 180}

        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="point",
            geometry=geometry,
            label="pixel_anomaly",
        )

        assert ann_id > 0

        annotation = manager.get_annotation(ann_id)
        assert annotation["annotation_type"] == "point"
        assert annotation["geometry"] == geometry

    def test_add_classification_annotation(self, populated_database):
        """Should add classification annotation without geometry."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="false_positive",
            category="data_issues",
            confidence=0.95,
        )

        assert ann_id > 0

        annotation = manager.get_annotation(ann_id)
        assert annotation["annotation_type"] == "classification"
        assert annotation["geometry"] is None
        assert annotation["label"] == "false_positive"
        assert annotation["confidence"] == 0.95

    def test_add_annotation_invalid_type(self, populated_database):
        """Should raise error for invalid annotation type."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        with pytest.raises(ValueError, match="Invalid annotation_type"):
            manager.add_annotation(
                result_id=result_ids[0],
                annotation_type="invalid_type",
                label="test",
            )

    def test_add_annotation_missing_geometry(self, populated_database):
        """Should raise error when geometry is missing for non-classification types."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        with pytest.raises(ValueError, match="geometry is required"):
            manager.add_annotation(
                result_id=result_ids[0],
                annotation_type="bounding_box",
                label="test",
            )

    def test_get_annotation_not_found(self, populated_database):
        """Should return None for non-existent annotation."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        annotation = manager.get_annotation(99999)
        assert annotation is None

    def test_get_annotations_for_result(self, populated_database):
        """Should get all annotations for a specific result."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Add multiple annotations to same result
        geometry1 = {"x": 10, "y": 20, "width": 50, "height": 60}
        geometry2 = {"x": 100, "y": 150, "width": 80, "height": 90}

        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="bounding_box",
            geometry=geometry1,
            label="artifact_1",
        )

        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="bounding_box",
            geometry=geometry2,
            label="artifact_2",
        )

        annotations = manager.get_annotations_for_result(result_ids[0])
        assert len(annotations) == 2
        assert all(ann["result_id"] == result_ids[0] for ann in annotations)

    def test_get_annotations_for_run(self, populated_database):
        """Should get all annotations for results in a run."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Add annotations to different results in same run
        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="issue_1",
        )

        manager.add_annotation(
            result_id=result_ids[1],
            annotation_type="classification",
            label="issue_2",
        )

        annotations = manager.get_annotations_for_run(run_id)
        assert len(annotations) == 2
        # Should include filename from results table
        assert "filename" in annotations[0]
        assert "subdirectory" in annotations[0]

    def test_update_annotation(self, populated_database):
        """Should update annotation fields."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Create annotation
        geometry = {"x": 10, "y": 20, "width": 50, "height": 60}
        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="bounding_box",
            geometry=geometry,
            label="initial_label",
            confidence=0.5,
        )

        # Update fields
        new_geometry = {"x": 15, "y": 25, "width": 55, "height": 65}
        success = manager.update_annotation(
            annotation_id=ann_id,
            geometry=new_geometry,
            label="updated_label",
            confidence=0.9,
            notes="Updated annotation",
        )

        assert success is True

        # Verify update
        annotation = manager.get_annotation(ann_id)
        assert annotation["geometry"] == new_geometry
        assert annotation["label"] == "updated_label"
        assert annotation["confidence"] == 0.9
        assert annotation["notes"] == "Updated annotation"

    def test_update_annotation_partial(self, populated_database):
        """Should update only specified fields."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Create annotation
        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="original_label",
            category="original_category",
        )

        # Update only label
        manager.update_annotation(annotation_id=ann_id, label="new_label")

        annotation = manager.get_annotation(ann_id)
        assert annotation["label"] == "new_label"
        assert annotation["category"] == "original_category"  # Unchanged

    def test_update_annotation_not_found(self, populated_database):
        """Should return False for non-existent annotation."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        success = manager.update_annotation(annotation_id=99999, label="test")
        assert success is False

    def test_delete_annotation(self, populated_database):
        """Should delete annotation successfully."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Create annotation
        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="to_delete",
        )

        # Delete annotation
        success = manager.delete_annotation(ann_id)
        assert success is True

        # Verify deletion
        annotation = manager.get_annotation(ann_id)
        assert annotation is None

    def test_delete_annotation_not_found(self, populated_database):
        """Should return False for non-existent annotation."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        success = manager.delete_annotation(99999)
        assert success is False

    def test_get_annotations_by_label(self, populated_database):
        """Should get annotations by label."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Add annotations with same label
        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="artifact",
        )

        manager.add_annotation(
            result_id=result_ids[1],
            annotation_type="classification",
            label="artifact",
        )

        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="other_label",
        )

        annotations = manager.get_annotations_by_label("artifact")
        assert len(annotations) == 2
        assert all(ann["label"] == "artifact" for ann in annotations)

    def test_get_annotations_by_category(self, populated_database):
        """Should get annotations by category."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Add annotations with same category
        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="issue_1",
            category="rendering_issues",
        )

        manager.add_annotation(
            result_id=result_ids[1],
            annotation_type="classification",
            label="issue_2",
            category="rendering_issues",
        )

        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="false_positive",
            category="data_issues",
        )

        annotations = manager.get_annotations_by_category("rendering_issues")
        assert len(annotations) == 2
        assert all(ann["category"] == "rendering_issues" for ann in annotations)

    def test_get_annotation_statistics(self, populated_database):
        """Should get annotation statistics."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        # Add various annotations
        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="bounding_box",
            geometry={"x": 10, "y": 20, "width": 50, "height": 60},
            label="artifact_1",
            category="rendering_issues",
            annotator_name="user1",
        )

        manager.add_annotation(
            result_id=result_ids[1],
            annotation_type="polygon",
            geometry={"points": [{"x": 10, "y": 20}, {"x": 30, "y": 40}, {"x": 15, "y": 50}]},
            label="artifact_2",
            category="rendering_issues",
            annotator_name="user2",
        )

        manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="false_positive",
            category="data_issues",
            annotator_name="user1",
        )

        stats = manager.get_annotation_statistics()

        assert stats["total_annotations"] == 3
        assert stats["by_type"]["bounding_box"] == 1
        assert stats["by_type"]["polygon"] == 1
        assert stats["by_type"]["classification"] == 1
        assert stats["by_category"]["rendering_issues"] == 2
        assert stats["by_category"]["data_issues"] == 1
        assert "artifact_1" in stats["unique_labels"]
        assert "artifact_2" in stats["unique_labels"]
        assert "false_positive" in stats["unique_labels"]
        assert "user1" in stats["annotators"]
        assert "user2" in stats["annotators"]

    def test_validate_bounding_box_geometry(self, temp_database):
        """Should validate bounding box geometry."""
        manager = AnnotationManager(temp_database)

        # Valid geometry
        valid = {"x": 10, "y": 20, "width": 100, "height": 50}
        assert manager.validate_geometry("bounding_box", valid) is True

        # Missing field
        invalid = {"x": 10, "y": 20, "width": 100}
        assert manager.validate_geometry("bounding_box", invalid) is False

    def test_validate_polygon_geometry(self, temp_database):
        """Should validate polygon geometry."""
        manager = AnnotationManager(temp_database)

        # Valid geometry (3+ points)
        valid = {
            "points": [
                {"x": 10, "y": 20},
                {"x": 30, "y": 40},
                {"x": 15, "y": 50},
            ]
        }
        assert manager.validate_geometry("polygon", valid) is True

        # Too few points
        invalid = {"points": [{"x": 10, "y": 20}, {"x": 30, "y": 40}]}
        assert manager.validate_geometry("polygon", invalid) is False

        # Missing points key
        invalid = {"vertices": [{"x": 10, "y": 20}]}
        assert manager.validate_geometry("polygon", invalid) is False

    def test_validate_point_geometry(self, temp_database):
        """Should validate point geometry."""
        manager = AnnotationManager(temp_database)

        # Valid geometry
        valid = {"x": 100, "y": 200}
        assert manager.validate_geometry("point", valid) is True

        # Missing field
        invalid = {"x": 100}
        assert manager.validate_geometry("point", invalid) is False

    def test_validate_classification_geometry(self, temp_database):
        """Should validate classification (no geometry required)."""
        manager = AnnotationManager(temp_database)

        # No geometry required
        assert manager.validate_geometry("classification", {}) is True
        assert manager.validate_geometry("classification", {"any": "data"}) is True

    def test_empty_result_annotations(self, populated_database):
        """Should return empty list for result with no annotations."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        annotations = manager.get_annotations_for_result(result_ids[0])
        assert annotations == []

    def test_annotation_with_confidence_score(self, populated_database):
        """Should store and retrieve confidence score."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)

        ann_id = manager.add_annotation(
            result_id=result_ids[0],
            annotation_type="classification",
            label="ml_prediction",
            confidence=0.87,
        )

        annotation = manager.get_annotation(ann_id)
        assert annotation["confidence"] == 0.87
