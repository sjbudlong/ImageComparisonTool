"""
Test script for annotation system.
"""
import sys
from pathlib import Path

# Add ImageComparisonSystem to path
sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonSystem.history import Database
from ImageComparisonSystem.annotations import AnnotationManager, ExportManager

print("=" * 70)
print("Annotation System Test")
print("=" * 70)

# Find an existing database or use a test one
db_path = Path(".imgcomp_history/comparison_history.db")

if not db_path.exists():
    print(f"\n⚠️  Database not found at {db_path}")
    print("\nSearching for databases in examples directory...")

    # Search for databases
    example_db = Path("examples/historicaldata/comparison_history.db")
    if example_db.exists():
        db_path = example_db
        print(f"✓ Found database: {db_path}")
    else:
        print("\n❌ No database found. Please run a comparison first with:")
        print("  python -m ImageComparisonSystem.main --base-dir ./examples --enable-history")
        sys.exit(1)

# Initialize managers
print(f"\nUsing database: {db_path}")
db = Database(db_path)
manager = AnnotationManager(db)

print("\n" + "=" * 70)
print("Annotation Manager Initialized")
print("=" * 70)

# Get statistics
stats = manager.get_annotation_statistics()
print(f"\nCurrent Statistics:")
print(f"  Total annotations: {stats['total_annotations']}")
print(f"  By type: {stats['by_type']}")
print(f"  By category: {stats['by_category']}")
print(f"  Unique labels: {stats['unique_labels']}")
print(f"  Annotators: {stats['annotators']}")

# Get recent results to annotate
print("\n" + "=" * 70)
print("Recent Comparison Results")
print("=" * 70)

results = db.execute_query(
    """SELECT result_id, filename, ssim, run_id
    FROM results
    ORDER BY result_id DESC
    LIMIT 5"""
)

if results:
    print(f"\nFound {len(results)} recent results:")
    for result in results:
        print(f"  - Result {result['result_id']}: {result['filename']} (SSIM: {result['ssim']:.4f})")

    # Demonstrate adding an annotation to the first result
    if stats['total_annotations'] == 0:
        print("\n" + "=" * 70)
        print("Adding Test Annotation")
        print("=" * 70)

        first_result = results[0]

        # Add a bounding box annotation
        geometry = {
            "x": 100,
            "y": 200,
            "width": 150,
            "height": 100
        }

        ann_id = manager.add_annotation(
            result_id=first_result['result_id'],
            annotation_type="bounding_box",
            geometry=geometry,
            label="test_artifact",
            category="testing",
            annotator_name="automated_test",
            confidence=0.95,
            notes="Test annotation created by test script"
        )

        print(f"\n✓ Created annotation {ann_id}")
        print(f"  Type: bounding_box")
        print(f"  Label: test_artifact")
        print(f"  Geometry: x={geometry['x']}, y={geometry['y']}, w={geometry['width']}, h={geometry['height']}")

        # Retrieve it
        annotation = manager.get_annotation(ann_id)
        print(f"\n✓ Retrieved annotation:")
        print(f"  ID: {annotation['annotation_id']}")
        print(f"  Result: {annotation['result_id']}")
        print(f"  Type: {annotation['annotation_type']}")
        print(f"  Label: {annotation['label']}")
        print(f"  Category: {annotation['category']}")
        print(f"  Confidence: {annotation['confidence']}")
        print(f"  Annotator: {annotation['annotator_name']}")
        print(f"  Notes: {annotation['notes']}")
        print(f"  Geometry: {annotation['geometry']}")

        # Update statistics
        stats = manager.get_annotation_statistics()
        print(f"\n✓ Updated statistics:")
        print(f"  Total annotations: {stats['total_annotations']}")
        print(f"  By type: {stats['by_type']}")
    else:
        print(f"\n✓ Database already has {stats['total_annotations']} annotations")

        # Show some existing annotations
        print("\n" + "=" * 70)
        print("Existing Annotations")
        print("=" * 70)

        for result in results[:3]:
            annotations = manager.get_annotations_for_result(result['result_id'])
            if annotations:
                print(f"\n{result['filename']} (Result {result['result_id']}):")
                for ann in annotations:
                    print(f"  - [{ann['annotation_type']}] {ann['label']} (confidence: {ann.get('confidence', 'N/A')})")
                    if ann['geometry']:
                        if ann['annotation_type'] == 'bounding_box':
                            g = ann['geometry']
                            print(f"    Box: x={g['x']}, y={g['y']}, w={g['width']}, h={g['height']}")

else:
    print("\n⚠️  No results found in database")
    print("Run a comparison first to generate results.")

# Test export manager
print("\n" + "=" * 70)
print("Export Manager")
print("=" * 70)

export_mgr = ExportManager(db, base_dir=Path("."))
print("✓ Export manager initialized")
print("\nAvailable export formats:")
print("  - COCO: JSON format for object detection")
print("  - YOLO: Text files for YOLO models")

# Get runs with annotations
runs = db.execute_query(
    """SELECT DISTINCT r.run_id, r.build_number, COUNT(a.annotation_id) as ann_count
    FROM runs r
    JOIN results res ON r.run_id = res.run_id
    LEFT JOIN annotations a ON res.result_id = a.result_id
    GROUP BY r.run_id
    ORDER BY r.run_id DESC
    LIMIT 5"""
)

if runs:
    print(f"\n✓ Found {len(runs)} runs:")
    for run in runs:
        print(f"  - Run {run['run_id']} ({run['build_number']}): {run['ann_count']} annotations")

    # Export example (if annotations exist)
    if stats['total_annotations'] > 0:
        run_to_export = runs[0]['run_id']
        output_coco = Path(f"annotations_run_{run_to_export}_coco.json")
        output_yolo = Path(f"annotations_run_{run_to_export}_yolo")

        print(f"\nExample export commands:")
        print(f"  COCO: export_mgr.export(run_id={run_to_export}, format='coco', output_path=Path('{output_coco}'))")
        print(f"  YOLO: export_mgr.export(run_id={run_to_export}, format='yolo', output_path=Path('{output_yolo}'))")

print("\n" + "=" * 70)
print("✓ Annotation System Test Complete")
print("=" * 70)
