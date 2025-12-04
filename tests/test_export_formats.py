"""
Unit tests for annotation export formats.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from ImageComparisonSystem.history.database import Database
from ImageComparisonSystem.annotations.annotation_manager import AnnotationManager
from ImageComparisonSystem.annotations.export_formats import (
    COCOExporter,
    YOLOExporter,
    ExportManager,
)


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
        (
            "test-build",
            datetime.now().isoformat(),
            "/test",
            "/test/new",
            "/test/known",
            "{}",
            10,
            5.0,
        ),
    )

    # Insert test results
    result_id_1 = db.execute_insert(
        """INSERT INTO results (run_id, filename, subdirectory, new_image_path, known_good_path,
           pixel_difference, ssim_score, composite_score, is_anomaly)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_id,
            "image1.png",
            "",
            "/test/new/image1.png",
            "/test/known/image1.png",
            10.0,
            0.8,
            50.0,
            0,
        ),
    )

    result_id_2 = db.execute_insert(
        """INSERT INTO results (run_id, filename, subdirectory, new_image_path, known_good_path,
           pixel_difference, ssim_score, composite_score, is_anomaly)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_id,
            "image2.png",
            "subdir",
            "/test/new/subdir/image2.png",
            "/test/known/subdir/image2.png",
            5.0,
            0.9,
            20.0,
            1,
        ),
    )

    return db, run_id, [result_id_1, result_id_2]


@pytest.fixture
def annotated_database(populated_database):
    """Create a database with annotations."""
    db, run_id, result_ids = populated_database
    manager = AnnotationManager(db)

    # Add bounding box annotation to first image
    ann_id_1 = manager.add_annotation(
        result_id=result_ids[0],
        annotation_type="bounding_box",
        geometry={"x": 100, "y": 200, "width": 150, "height": 100},
        label="artifact_1",
        category="rendering_issues",
    )

    # Add polygon annotation to first image
    ann_id_2 = manager.add_annotation(
        result_id=result_ids[0],
        annotation_type="polygon",
        geometry={
            "points": [
                {"x": 10, "y": 20},
                {"x": 50, "y": 30},
                {"x": 40, "y": 80},
                {"x": 15, "y": 70},
            ]
        },
        label="artifact_2",
    )

    # Add bounding box annotation to second image (for YOLO export)
    ann_id_3 = manager.add_annotation(
        result_id=result_ids[1],
        annotation_type="bounding_box",
        geometry={"x": 250, "y": 180, "width": 100, "height": 80},
        label="artifact_3",
        category="rendering_issues",
    )

    # Add point annotation to second image
    ann_id_4 = manager.add_annotation(
        result_id=result_ids[1],
        annotation_type="point",
        geometry={"x": 250, "y": 180},
        label="pixel_issue",
    )

    # Add classification annotation to second image
    ann_id_5 = manager.add_annotation(
        result_id=result_ids[1],
        annotation_type="classification",
        label="false_positive",
        confidence=0.95,
    )

    return db, run_id, result_ids, [ann_id_1, ann_id_2, ann_id_3, ann_id_4, ann_id_5]


@pytest.mark.unit
class TestCOCOExporter:
    """Test COCOExporter class."""

    def test_initialization(self, populated_database):
        """COCOExporter should initialize with manager and base_dir."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        assert exporter.annotation_manager is not None
        assert exporter.base_dir == Path("/test")

    def test_export_run_no_annotations(self, populated_database):
        """Export should handle runs with no annotations."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            result = exporter.export_run(run_id, output_path)

            assert result["success"] is False
            assert result["annotation_count"] == 0
            assert result["image_count"] == 0

    def test_export_run_with_annotations(self, annotated_database):
        """Export should create valid COCO JSON file."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            result = exporter.export_run(run_id, output_path)

            assert result["success"] is True
            assert result["annotation_count"] == 5  # 5 annotations total
            assert result["image_count"] == 2  # 2 images
            assert result["category_count"] > 0

            # Verify file was created
            assert output_path.exists()

            # Verify JSON structure
            with open(output_path) as f:
                coco_data = json.load(f)

            assert "info" in coco_data
            assert "images" in coco_data
            assert "annotations" in coco_data
            assert "categories" in coco_data

            assert len(coco_data["images"]) == 2
            assert len(coco_data["annotations"]) == 5
            assert len(coco_data["categories"]) > 0

    def test_coco_structure_validity(self, annotated_database):
        """COCO output should have valid structure."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            exporter.export_run(run_id, output_path)

            with open(output_path) as f:
                coco_data = json.load(f)

            # Check info section
            assert "description" in coco_data["info"]
            assert "version" in coco_data["info"]

            # Check images
            for image in coco_data["images"]:
                assert "id" in image
                assert "file_name" in image
                assert "width" in image
                assert "height" in image

            # Check annotations
            for ann in coco_data["annotations"]:
                assert "id" in ann
                assert "image_id" in ann
                assert "category_id" in ann
                assert "iscrowd" in ann

            # Check categories
            for cat in coco_data["categories"]:
                assert "id" in cat
                assert "name" in cat

    def test_bounding_box_conversion(self, annotated_database):
        """Bounding box should convert to COCO bbox format."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            exporter.export_run(run_id, output_path)

            with open(output_path) as f:
                coco_data = json.load(f)

            # Find bounding box annotation (first one)
            bbox_ann = coco_data["annotations"][0]
            assert "bbox" in bbox_ann
            assert len(bbox_ann["bbox"]) == 4  # [x, y, width, height]
            assert bbox_ann["bbox"] == [100, 200, 150, 100]
            assert "area" in bbox_ann
            assert bbox_ann["area"] == 15000  # 150 * 100

    def test_polygon_conversion(self, annotated_database):
        """Polygon should convert to COCO segmentation format."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            exporter.export_run(run_id, output_path)

            with open(output_path) as f:
                coco_data = json.load(f)

            # Find polygon annotation (second one)
            poly_ann = coco_data["annotations"][1]
            assert "segmentation" in poly_ann
            assert isinstance(poly_ann["segmentation"], list)
            assert len(poly_ann["segmentation"]) == 1  # Single polygon
            # Should have 8 coordinates (4 points * 2)
            assert len(poly_ann["segmentation"][0]) == 8

            # Should also have bbox calculated from polygon
            assert "bbox" in poly_ann
            assert "area" in poly_ann

    def test_point_conversion(self, annotated_database):
        """Point should convert to tiny COCO bbox."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            exporter.export_run(run_id, output_path)

            with open(output_path) as f:
                coco_data = json.load(f)

            # Find point annotation (fourth one, after 2 bboxes and 1 polygon)
            point_ann = coco_data["annotations"][3]
            assert "bbox" in point_ann
            assert point_ann["bbox"] == [250, 180, 1, 1]  # 1x1 bbox
            assert point_ann["area"] == 1

    def test_export_without_metadata(self, annotated_database):
        """Export should support disabling metadata."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            exporter.export_run(run_id, output_path, include_metadata=False)

            with open(output_path) as f:
                coco_data = json.load(f)

            assert coco_data["info"] == {}

    def test_category_generation(self, annotated_database):
        """Categories should be generated from unique labels."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = COCOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            exporter.export_run(run_id, output_path)

            with open(output_path) as f:
                coco_data = json.load(f)

            categories = coco_data["categories"]
            labels = [cat["name"] for cat in categories]

            assert "artifact_1" in labels
            assert "artifact_2" in labels
            assert "pixel_issue" in labels
            assert "false_positive" in labels


@pytest.mark.unit
class TestYOLOExporter:
    """Test YOLOExporter class."""

    def test_initialization(self, populated_database):
        """YOLOExporter should initialize with manager and base_dir."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        assert exporter.annotation_manager is not None
        assert exporter.base_dir == Path("/test")

    def test_export_run_no_annotations(self, populated_database):
        """Export should handle runs with no annotations."""
        db, run_id, result_ids = populated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            result = exporter.export_run(run_id, output_dir)

            assert result["success"] is False
            assert result["file_count"] == 0
            assert result["annotation_count"] == 0

    def test_export_run_with_annotations(self, annotated_database):
        """Export should create YOLO label files."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            result = exporter.export_run(
                run_id, output_dir, image_width=1920, image_height=1080
            )

            assert result["success"] is True
            assert result["file_count"] == 2  # 2 images with annotations
            assert result["annotation_count"] >= 2  # At least bbox and polygon
            assert result["class_count"] > 0

            # Verify directory was created
            assert output_dir.exists()

            # Verify label files exist
            assert (output_dir / "image1.txt").exists()
            assert (output_dir / "image2.txt").exists()

            # Verify classes.txt exists
            assert (output_dir / "classes.txt").exists()

    def test_yolo_format_validity(self, annotated_database):
        """YOLO format should have valid normalized coordinates."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            exporter.export_run(run_id, output_dir, image_width=1920, image_height=1080)

            # Read first label file
            with open(output_dir / "image1.txt") as f:
                lines = f.readlines()

            assert len(lines) >= 2  # At least bbox and polygon

            # Parse first line (bounding box)
            parts = lines[0].strip().split()
            assert len(parts) == 5  # class_id x_center y_center width height

            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

            # All values should be in [0, 1] range
            assert 0.0 <= x_center <= 1.0
            assert 0.0 <= y_center <= 1.0
            assert 0.0 <= width <= 1.0
            assert 0.0 <= height <= 1.0

    def test_bounding_box_normalization(self, annotated_database):
        """Bounding box coordinates should be correctly normalized."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            exporter.export_run(run_id, output_dir, image_width=1920, image_height=1080)

            with open(output_dir / "image1.txt") as f:
                line = f.readline().strip()

            parts = line.split()
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

            # Original bbox: x=100, y=200, w=150, h=100
            # Center: x=175, y=250
            # Normalized: x=175/1920, y=250/1080, w=150/1920, h=100/1080
            expected_x = 175.0 / 1920.0
            expected_y = 250.0 / 1080.0
            expected_w = 150.0 / 1920.0
            expected_h = 100.0 / 1080.0

            assert abs(x_center - expected_x) < 0.0001
            assert abs(y_center - expected_y) < 0.0001
            assert abs(width - expected_w) < 0.0001
            assert abs(height - expected_h) < 0.0001

    def test_polygon_to_bbox_conversion(self, annotated_database):
        """Polygon should convert to bounding box for YOLO."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            exporter.export_run(run_id, output_dir, image_width=1920, image_height=1080)

            with open(output_dir / "image1.txt") as f:
                lines = f.readlines()

            # Second line should be the polygon converted to bbox
            assert len(lines) >= 2
            parts = lines[1].strip().split()
            assert len(parts) == 5

    def test_classes_file_generation(self, annotated_database):
        """classes.txt should contain all unique labels."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            exporter.export_run(run_id, output_dir)

            with open(output_dir / "classes.txt") as f:
                classes = f.read().strip().split("\n")

            assert "artifact_1" in classes
            assert "artifact_2" in classes
            assert "pixel_issue" in classes
            assert "false_positive" in classes

    def test_skip_classes_file(self, annotated_database):
        """Export should support skipping classes.txt generation."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            exporter.export_run(run_id, output_dir, generate_classes_file=False)

            assert not (output_dir / "classes.txt").exists()

    def test_custom_image_dimensions(self, annotated_database):
        """Export should support custom image dimensions."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = AnnotationManager(db)
        exporter = YOLOExporter(manager, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            exporter.export_run(run_id, output_dir, image_width=640, image_height=480)

            with open(output_dir / "image1.txt") as f:
                line = f.readline().strip()

            parts = line.split()
            # Coordinates should be normalized differently
            assert 0.0 <= float(parts[1]) <= 1.0


@pytest.mark.unit
class TestExportManager:
    """Test ExportManager class."""

    def test_initialization(self, populated_database):
        """ExportManager should initialize with database and base_dir."""
        db, run_id, result_ids = populated_database
        manager = ExportManager(db, Path("/test"))

        assert manager.database is not None
        assert manager.base_dir == Path("/test")
        assert manager.annotation_manager is not None

    def test_export_coco_format(self, annotated_database):
        """Export should support COCO format."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = ExportManager(db, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "annotations.json"
            result = manager.export(run_id, "coco", output_path)

            assert result["success"] is True
            assert output_path.exists()

    def test_export_yolo_format(self, annotated_database):
        """Export should support YOLO format."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = ExportManager(db, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "labels"
            result = manager.export(run_id, "yolo", output_dir)

            assert result["success"] is True
            assert output_dir.exists()

    def test_export_invalid_format(self, annotated_database):
        """Export should raise error for invalid format."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = ExportManager(db, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output"
            with pytest.raises(ValueError, match="Unsupported export format"):
                manager.export(run_id, "invalid_format", output_path)

    def test_export_with_kwargs(self, annotated_database):
        """Export should pass kwargs to specific exporters."""
        db, run_id, result_ids, ann_ids = annotated_database
        manager = ExportManager(db, Path("/test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test COCO with include_metadata=False
            output_path = Path(tmpdir) / "annotations.json"
            result = manager.export(run_id, "coco", output_path, include_metadata=False)
            assert result["success"] is True

            # Test YOLO with custom dimensions
            output_dir = Path(tmpdir) / "labels"
            result = manager.export(
                run_id, "yolo", output_dir, image_width=640, image_height=480
            )
            assert result["success"] is True
