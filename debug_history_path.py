"""
Debug script to understand history database path resolution.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonSystem.config import Config

print("=" * 70)
print("History Database Path Resolution Debug")
print("=" * 70)

# Test various path configurations
test_cases = [
    ("No custom path (default)", None),
    ("Relative directory", "examples/historicaldata"),
    ("Relative file path", "examples/historicaldata/comparison_history.db"),
    ("Absolute directory", str(Path("D:/GitRepos/ImageComparisonTool/examples/historicaldata").absolute())),
    ("Absolute file path", str(Path("D:/GitRepos/ImageComparisonTool/examples/historicaldata/comparison_history.db").absolute())),
]

base_dir = Path(".")

for description, history_db_path in test_cases:
    print(f"\n{description}:")
    print(f"  Input: {history_db_path}")

    try:
        config = Config(
            base_dir=base_dir,
            new_dir="new",
            known_good_dir="known_good",
            enable_history=True,
            history_db_path=history_db_path
        )

        # Simulate HistoryManager path resolution
        if config.history_db_path:
            db_path = Path(config.history_db_path)
        else:
            history_dir = config.base_dir / ".imgcomp_history"
            db_path = history_dir / "comparison_history.db"

        print(f"  Resolved to: {db_path.absolute()}")
        print(f"  Parent dir: {db_path.parent.absolute()}")
        print(f"  Parent exists: {db_path.parent.exists()}")
        print(f"  DB exists: {db_path.exists()}")

    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 70)
print("Guidelines for History DB Path:")
print("=" * 70)
print("""
The history_db_path can be:
1. Empty/None: Uses default <base_dir>/.imgcomp_history/comparison_history.db
2. Directory path: Will create comparison_history.db inside that directory
3. File path: Will use that exact file path

IMPORTANT: The path you enter in the GUI should be the FULL PATH to either:
  - A directory (e.g., D:\\GitRepos\\ImageComparisonTool\\examples\\historicaldata)
  - A database file (e.g., D:\\GitRepos\\ImageComparisonTool\\examples\\historicaldata\\comparison_history.db)

If you enter a directory, the system expects you want to create the database IN that directory.
If you enter a file path ending in .db, it will use that exact file.

Current behavior:
  - If history_db_path is set, it uses that path directly
  - If it's a directory, you need to include the filename
  - Parent directory will be created automatically
""")

print("\n" + "=" * 70)
print("What to Enter in UI:")
print("=" * 70)
print("""
For your case (D:\\GitRepos\\ImageComparisonTool\\examples\\historicaldata):

Option 1 - Enter full file path:
  D:\\GitRepos\\ImageComparisonTool\\examples\\historicaldata\\comparison_history.db

Option 2 - Enter relative file path from base_dir:
  examples/historicaldata/comparison_history.db

Option 3 - Leave empty to use default:
  (empty) → creates in <base_dir>/.imgcomp_history/comparison_history.db
""")
