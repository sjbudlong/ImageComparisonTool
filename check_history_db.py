"""
Check if history database exists and show its location.
"""
import sys
from pathlib import Path

print("=" * 70)
print("History Database Checker")
print("=" * 70)

# Search for all comparison_history.db files
print("\nSearching for history databases...")

# Search common locations
search_paths = [
    Path.cwd(),  # Current directory
    Path(__file__).parent,  # Script directory
    Path.home(),  # Home directory
]

found_databases = []

for search_path in search_paths:
    try:
        # Search recursively for comparison_history.db
        for db_file in search_path.rglob("comparison_history.db"):
            found_databases.append(db_file)
            print(f"  Found: {db_file}")
    except PermissionError:
        # Skip directories we don't have permission to read
        pass

# Also search for .imgcomp_history directories
print("\nSearching for .imgcomp_history directories...")
found_dirs = []

for search_path in search_paths:
    try:
        for history_dir in search_path.rglob(".imgcomp_history"):
            if history_dir.is_dir():
                found_dirs.append(history_dir)
                print(f"  Found: {history_dir}")

                # Check if it has a database file
                db_file = history_dir / "comparison_history.db"
                if db_file.exists():
                    print(f"    ✓ Database exists: {db_file}")
                    print(f"    Size: {db_file.stat().st_size} bytes")
                else:
                    print(f"    ✗ No database file found")
    except PermissionError:
        pass

print("\n" + "=" * 70)
print("Summary:")
print("=" * 70)
print(f"Databases found: {len(found_databases)}")
print(f"History directories found: {len(found_dirs)}")

if found_databases:
    print("\n✅ Database files found at:")
    for db in found_databases:
        print(f"  - {db.absolute()}")

        # Check contents
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from ImageComparisonSystem.history import Database

            db_obj = Database(db)
            run_count = db_obj.get_row_count("runs")
            result_count = db_obj.get_row_count("results")

            print(f"    Runs: {run_count}")
            print(f"    Results: {result_count}")

            if run_count > 0:
                runs = db_obj.execute_query(
                    "SELECT build_number, total_images, timestamp FROM runs ORDER BY timestamp DESC LIMIT 3"
                )
                print(f"    Recent runs:")
                for run in runs:
                    print(f"      - {run['build_number']}: {run['total_images']} images at {run['timestamp']}")
        except Exception as e:
            print(f"    Error reading database: {e}")
else:
    print("\n⚠️  No history databases found!")
    print("\nThis could mean:")
    print("  1. No comparisons have been run yet with history enabled")
    print("  2. The database is in a different location")
    print("  3. The comparison failed before creating the database")

    print("\nTo create a database, run a comparison with:")
    print("  --enable-history (enabled by default)")
    print("  --base-dir <your_directory>")

    print("\nThe database will be created at:")
    print("  <base_dir>/.imgcomp_history/comparison_history.db")

print("\n" + "=" * 70)
print("What's your configuration?")
print("=" * 70)
print("\nPlease tell me:")
print("  1. What base_dir are you using?")
print("  2. Are you setting --history-db-path?")
print("  3. How are you running the comparison? (GUI or CLI)")
