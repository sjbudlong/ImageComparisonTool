"""
Test script to verify historical database creation.
"""
import sys
from pathlib import Path
import tempfile
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)-8s] %(name)s - %(message)s')

# Add ImageComparisonSystem to path
sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonSystem.config import Config
from ImageComparisonSystem.comparator import ImageComparator
import numpy as np
from PIL import Image

def create_test_images(base_dir: Path):
    """Create test images for comparison."""
    # Create directories
    new_dir = base_dir / "new"
    known_good_dir = base_dir / "known_good"
    new_dir.mkdir(parents=True, exist_ok=True)
    known_good_dir.mkdir(parents=True, exist_ok=True)

    # Create identical test images
    img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))

    img.save(new_dir / "test1.png")
    img.save(known_good_dir / "test1.png")

    print(f"Created test images in {base_dir}")
    print(f"  - {new_dir / 'test1.png'}")
    print(f"  - {known_good_dir / 'test1.png'}")

def test_history_creation():
    """Test if historical database is created."""
    print("=" * 70)
    print("Testing Historical Database Creation")
    print("=" * 70)

    # Use temp directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir) / "test_comparison"
        base_dir.mkdir()

        print(f"\nBase directory: {base_dir}")

        # Create test images
        create_test_images(base_dir)

        # Create config with history enabled
        print("\nCreating config with enable_history=True...")
        config = Config(
            base_dir=base_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_history=True,
            enable_flip=False  # Disable FLIP for faster test
        )

        print(f"Config created:")
        print(f"  enable_history: {config.enable_history}")
        print(f"  build_number: {config.build_number}")
        print(f"  history_db_path: {config.history_db_path}")

        # Create comparator (this should initialize history)
        print("\nCreating comparator...")
        comparator = ImageComparator(config)

        print(f"Comparator created:")
        print(f"  history_manager: {comparator.history_manager}")
        if comparator.history_manager:
            print(f"  db_path: {comparator.history_manager.db_path}")
            print(f"  db exists: {comparator.history_manager.db_path.exists()}")

        # Run comparison
        print("\nRunning comparison...")
        results = list(comparator.compare_all_streaming())
        print(f"Comparison complete: {len(results)} results")

        # Generate reports
        print("\nGenerating reports...")
        comparator._generate_reports(results)

        # Check if database was created
        history_dir = base_dir / ".imgcomp_history"
        db_path = history_dir / "comparison_history.db"

        print("\n" + "=" * 70)
        print("Results:")
        print("=" * 70)
        print(f"History directory exists: {history_dir.exists()}")
        print(f"Database file exists: {db_path.exists()}")

        if db_path.exists():
            print(f"Database path: {db_path}")
            print(f"Database size: {db_path.stat().st_size} bytes")

            # Check database contents
            from ImageComparisonSystem.history import Database
            db = Database(db_path)

            run_count = db.get_row_count("runs")
            result_count = db.get_row_count("results")

            print(f"\nDatabase contents:")
            print(f"  Runs: {run_count}")
            print(f"  Results: {result_count}")

            if run_count > 0:
                runs = db.execute_query("SELECT * FROM runs ORDER BY timestamp DESC LIMIT 1")
                for run in runs:
                    print(f"\nLatest run:")
                    print(f"  Run ID: {run['run_id']}")
                    print(f"  Build Number: {run['build_number']}")
                    print(f"  Total Images: {run['total_images']}")
                    print(f"  Timestamp: {run['timestamp']}")

            print("\n✅ SUCCESS: Database created and populated!")
        else:
            print("\n❌ FAILURE: Database was not created")
            print("\nPossible issues:")
            print("  1. History initialization failed (check logs above)")
            print("  2. Exception during comparison")
            print("  3. History not enabled properly")

if __name__ == "__main__":
    test_history_creation()
