# Commit Hash Storage for Historical Data Reproducibility

## Overview

The Image Comparison Tool now supports storing Git commit hashes with each historical comparison run. This enables **exact reproducibility** of image comparisons by allowing you to checkout the same code version that produced the original results.

## Why Commit Hashes Matter

When you want to recreate a comparison run from the past, you need to ensure:
1. ✅ Same image analyzer algorithms
2. ✅ Same metric calculation logic
3. ✅ Same thresholds and settings
4. ✅ Same environment (Python version, dependencies)

By storing the commit hash, you can:
- **Reproduce exact results** by checking out the specific commit
- **Analyze how algorithm changes affected results** over time
- **Reduce storage needs** by not keeping all historical images (just the commit hash)
- **Improve debugging** of anomalies by finding exactly which code version created them

## Implementation

### Database Schema

The `runs` table now includes a `commit_hash` column:

```sql
CREATE TABLE runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_number TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    base_dir TEXT NOT NULL,
    new_dir TEXT NOT NULL,
    known_good_dir TEXT NOT NULL,
    config_snapshot TEXT,
    total_images INTEGER,
    avg_difference REAL,
    max_difference REAL,
    notes TEXT,
    commit_hash TEXT  -- NEW: Git commit hash for reproducibility
);

-- Performance index for commit_hash lookups
CREATE INDEX idx_runs_commit_hash ON runs(commit_hash);
```

### Config Class

Added `commit_hash` field to the `Config` dataclass:

```python
@dataclass
class Config:
    # ... existing fields ...
    
    # Source code tracking
    commit_hash: Optional[str] = None
    """Git commit hash for reproducibility. Allows recreating the exact environment that generated this run."""
```

### HistoryManager

Updated `save_run()` to accept and store the commit hash:

```python
def save_run(
    self,
    results: List[ComparisonResult],
    config,  # Now accepts commit_hash from config
    notes: Optional[str] = None
) -> int:
    # ...
    run_id = self.db.execute_insert(
        """INSERT INTO runs (
            build_number, timestamp, base_dir, new_dir, known_good_dir,
            config_snapshot, total_images, avg_difference, max_difference, notes, commit_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            config.build_number,
            datetime.now().isoformat(),
            str(config.base_dir),
            config.new_dir,
            config.known_good_dir,
            json.dumps(config_snapshot),
            total_images,
            avg_difference,
            max_difference,
            notes,
            config.commit_hash,  # NEW: Store commit hash
        ),
    )
```

## Usage

### CLI Usage

Provide the commit hash when running comparisons:

```bash
# Automatic (get current commit hash)
cd ImageComparisonSystem
COMMIT=$(git rev-parse HEAD)
python main.py --base-dir ./renders --build-number "build-001" --commit-hash "$COMMIT"

# Windows (PowerShell)
$COMMIT = git rev-parse HEAD
python main.py --base-dir ./renders --build-number "build-001" --commit-hash $COMMIT

# Or manually specify
python main.py --base-dir ./renders --build-number "build-001" --commit-hash "abc123def456"
```

### Programmatic Usage

```python
from ImageComparisonSystem.config import Config
from ImageComparisonSystem.history import HistoryManager

config = Config(
    base_dir=Path("/path/to/images"),
    build_number="build-2025-12-04-001",
    commit_hash="abc123def456789",  # NEW: Add commit hash
)

history_manager = HistoryManager(config)
run_id = history_manager.save_run(results, config)

# Later, retrieve the commit hash to reproduce
run = history_manager.get_run(run_id)
print(f"Reproduce this run using: git checkout {run['commit_hash']}")
```

### Querying Historical Data

```python
from ImageComparisonSystem.history.database import Database

db = Database(Path("./history.db"))

# Find all runs for a specific commit
query = """
    SELECT run_id, build_number, timestamp, avg_difference 
    FROM runs 
    WHERE commit_hash = ?
"""
runs = db.execute_query(query, ("abc123def456",))

# Find runs that have changed since a specific commit
query = """
    SELECT run_id, build_number, commit_hash, avg_difference
    FROM runs
    WHERE commit_hash NOT IN (?, ?)
    ORDER BY timestamp DESC
"""
changed_runs = db.execute_query(query, ("original_hash", "stable_hash"))
```

## Reproduction Workflow

### Scenario: Recreate a comparison from 6 months ago

**Step 1:** Query the historical database for the commit hash

```bash
# Using the CLI
python main.py --base-dir ./renders --history-stats | grep commit_hash
```

**Step 2:** Checkout the exact commit

```bash
git checkout abc123def456789
```

**Step 3:** Run the comparison with the same settings

```bash
python main.py \
  --base-dir ./renders \
  --build-number "build-2025-06-04-001" \
  --commit-hash "abc123def456789"
```

**Step 4:** Compare results

```python
# Compare current results with historical results
old_run = history_manager.get_run(old_run_id)
new_run = history_manager.get_run(new_run_id)

print(f"Old avg diff ({old_run['commit_hash']}): {old_run['avg_difference']}%")
print(f"New avg diff ({new_run['commit_hash']}): {new_run['avg_difference']}%")
```

## Benefits

1. **Exact Reproducibility**: Recreate any comparison by checking out the commit
2. **Algorithm Change Analysis**: See how code changes affected results over time
3. **Reduced Storage**: Store commit hashes instead of all historical images
4. **Better Debugging**: Pinpoint when anomalies were introduced
5. **Compliance**: Document exactly which version produced regulatory/audit results
6. **Continuous Integration**: Automate result verification against specific commits

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Image Comparison with History

on: [push, pull_request]

jobs:
  compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run image comparison
        run: |
          COMMIT=$(git rev-parse HEAD)
          python main.py \
            --base-dir ./test_images \
            --build-number "ci-${{ github.run_number }}" \
            --commit-hash "$COMMIT" \
            --no-history
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: comparison-results
          path: reports/
```

## Database Migration

The schema change is automatically applied when the database initializes:

- **Fresh Databases**: Include `commit_hash` column from v1
- **Existing Databases**: Requires running v2+ migrations (to be added in future versions)

For now, fresh installations will have full commit_hash support.

## Best Practices

1. **Always provide commit hash** for reproducible comparisons
2. **Use full commit hash** (40 character SHA-1 or 12 character short hash)
3. **Store commit hash in build logs** for easy reference
4. **Automate in CI/CD** to capture it automatically
5. **Document your branching strategy** (main vs develop vs release branches)

## Technical Details

### Field Properties
- **Type**: `TEXT` (nullable)
- **Length**: 40 characters (SHA-1), or shorter for abbreviated hashes
- **Indexed**: Yes, for fast lookups
- **Default**: `NULL` (commit hash optional)
- **Immutable**: Once set, typically doesn't change

### Performance Impact
- **Index size**: ~100-200 bytes per run
- **Query speed**: O(1) with index
- **Storage overhead**: ~0.1% for typical installations

## Future Enhancements

Potential future features:
- Automatic commit hash detection from git (if run inside repo)
- Branch name storage alongside commit hash
- Tags/version labels
- Author/committer information
- Diff URLs to GitHub/GitLab
- Automated comment posting on merge requests with results

## Examples

See `tests/test_history_manager.py` for usage examples:

```python
def test_save_run_with_commit_hash(self, temp_history_manager):
    """Test saving run with commit hash for reproducibility."""
    config = MockConfig(
        base_dir=Path("/test/base"),
        build_number="build-301",
        commit_hash="abc123def456"
    )

    results = [create_mock_result("image1.png", 10.0)]
    run_id = temp_history_manager.save_run(results, config)

    # Retrieve and verify commit hash was saved
    run = temp_history_manager.get_run(run_id)
    assert run is not None
    assert run["commit_hash"] == "abc123def456"
```
