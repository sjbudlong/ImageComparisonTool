"""
Script to find where historical database is/will be created.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonSystem.config import Config

print("=" * 70)
print("Historical Database Location Finder")
print("=" * 70)

# Example configurations
examples = [
    ("Current directory", ".", "new", "known_good"),
    ("Absolute path example", r"C:\my_images", "new", "known_good"),
    ("Relative path example", "./test_images", "new", "known_good"),
]

for description, base_dir, new_dir, kg_dir in examples:
    try:
        config = Config(
            base_dir=base_dir,
            new_dir=new_dir,
            known_good_dir=kg_dir,
            enable_history=True
        )

        # Determine where database would be created
        if config.history_db_path:
            db_path = Path(config.history_db_path)
        else:
            history_dir = config.base_dir / ".imgcomp_history"
            db_path = history_dir / "comparison_history.db"

        print(f"\n{description}:")
        print(f"  Base dir: {config.base_dir.absolute()}")
        print(f"  Database: {db_path.absolute()}")
        print(f"  Exists: {db_path.exists()}")

    except Exception as e:
        print(f"\n{description}: Error - {e}")

print("\n" + "=" * 70)
print("How to find your database:")
print("=" * 70)
print("\n1. Look in your comparison base directory")
print("2. Find the hidden folder: .imgcomp_history")
print("3. The database file: comparison_history.db")
print("\nExample commands:")
print("  Windows: dir /a <your_base_dir>\\.imgcomp_history")
print("  Linux/Mac: ls -la <your_base_dir>/.imgcomp_history")
print("\nTo search your entire system:")
print('  Windows: dir /s comparison_history.db')
print('  Linux/Mac: find ~ -name "comparison_history.db" 2>/dev/null')
