# Historical Database Creation Fix

**Date:** December 5, 2025
**Issue:** Historical database not being created
**Status:** ✅ **FIXED**

---

## Problem Summary

The historical database (`.imgcomp_history/comparison_history.db`) was not being created when running comparisons, even with `enable_history=True`.

---

## Root Causes

### Issue 1: Incorrect Database Initialization in Comparator

**File:** [comparator.py:54-67](../ImageComparisonSystem/comparator.py#L54-L67)

**Problem:**
```python
# OLD CODE (BROKEN)
if config.enable_history and HistoryManager is not None:
    try:
        db = Database(config.history_db_path)  # config.history_db_path is None!
        self.history_manager = HistoryManager(db, config)
```

The comparator was trying to create `Database(None)`, which would fail. The HistoryManager is designed to handle `None` db_path and create a default path, but the comparator wasn't using it correctly.

**Solution:**
```python
# NEW CODE (FIXED)
if config.enable_history and HistoryManager is not None:
    try:
        # HistoryManager handles database initialization and default path
        self.history_manager = HistoryManager(config)
        logger.info(f"History tracking enabled: {self.history_manager.db_path}")
```

### Issue 2: Missing Build Number Auto-Generation

**File:** [history_manager.py:92-97](../ImageComparisonSystem/history/history_manager.py#L92-L97)

**Problem:**
When `config.build_number` is `None` (the default), the database would store `NULL` for build_number, making it difficult to identify runs.

**Solution:**
Added auto-generation of build numbers:

```python
# Generate build number if not provided
build_number = config.build_number
if build_number is None:
    # Auto-generate build number from timestamp
    build_number = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Auto-generated build number: {build_number}")
```

---

## Changes Made

### 1. comparator.py

**Before:**
```python
# Initialize database
db = Database(config.history_db_path)
self.history_manager = HistoryManager(db, config)
logger.info(f"History tracking enabled: {config.history_db_path}")
```

**After:**
```python
# HistoryManager handles database initialization and default path
self.history_manager = HistoryManager(config)
logger.info(f"History tracking enabled: {self.history_manager.db_path}")
```

### 2. history_manager.py

Added auto-generation logic before inserting run record:

```python
# Generate build number if not provided
build_number = config.build_number
if build_number is None:
    # Auto-generate build number from timestamp
    build_number = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Auto-generated build number: {build_number}")

# Insert run record with build_number (not config.build_number)
run_id = self.db.execute_insert(
    """INSERT INTO runs (...) VALUES (...)""",
    (build_number, ...)  # Use generated build_number
)
```

---

## How It Works Now

### Automatic Database Creation

1. **No configuration needed**: History is enabled by default (`enable_history=True`)
2. **Default location**: `<base_dir>/.imgcomp_history/comparison_history.db`
3. **Auto-created**: Database and directory are created automatically on first run

### Build Number Handling

| Scenario | Build Number Used | Example |
|----------|------------------|---------|
| User provides `--build-number "v1.0"` | User's value | `v1.0` |
| User provides nothing | Auto-generated | `auto_20251205_143022` |
| GUI run (no build number) | Auto-generated | `auto_20251205_143125` |

### Auto-Generated Build Number Format

```
auto_YYYYMMDD_HHMMSS
```

Examples:
- `auto_20251205_143022` - Run on Dec 5, 2025 at 14:30:22
- `auto_20251205_151530` - Run on Dec 5, 2025 at 15:15:30

---

## Verification

### Check if Database Exists

After running a comparison:

```bash
# Windows
dir .imgcomp_history

# Linux/Mac
ls -la .imgcomp_history/
```

Expected output:
```
comparison_history.db
```

### Check Database Contents

```python
from ImageComparisonSystem.history import Database

db = Database(".imgcomp_history/comparison_history.db")

# Check run count
print(f"Total runs: {db.get_row_count('runs')}")

# Check results count
print(f"Total results: {db.get_row_count('results')}")

# View recent runs
runs = db.execute_query("SELECT * FROM runs ORDER BY timestamp DESC LIMIT 5")
for run in runs:
    print(f"Run {run['run_id']}: {run['build_number']} - {run['total_images']} images")
```

### Expected Log Output

When history is working correctly, you should see:

```
[INFO    ] ImageComparison - History tracking enabled: /path/to/.imgcomp_history/comparison_history.db
[INFO    ] ImageComparison - Auto-generated build number: auto_20251205_143022
[INFO    ] ImageComparison - Saving results to history database...
[INFO    ] ImageComparison - Results saved (run_id: 1)
[INFO    ] ImageComparison - Enriching results with historical analysis...
```

---

## Database Schema

The database contains 8 tables:

1. **runs** - Comparison run metadata (build_number, timestamp, config)
2. **results** - Individual image comparison results
3. **composite_metric_config** - Composite metric weight configurations
4. **retention_policy** - Data retention policies
5. **annotations** - User annotations on comparisons
6. **reviewer_metadata** - Reviewer information
7. **image_storage** - Image storage metadata
8. **sqlite_sequence** - SQLite auto-increment tracking

---

## Backward Compatibility

✅ **Fully backward compatible**

- Existing configurations with explicit `build_number` work unchanged
- Existing configurations without `build_number` now get auto-generated values
- Database location logic unchanged (uses `history_db_path` if provided, otherwise default)
- All existing queries and operations work as before

---

## Related Files

- **Database**: `ImageComparisonSystem/history/database.py`
- **History Manager**: `ImageComparisonSystem/history/history_manager.py`
- **Comparator**: `ImageComparisonSystem/comparator.py`
- **Config**: `ImageComparisonSystem/config.py`

---

## Common Issues & Solutions

### Issue: "Database not found"

**Cause**: Looking in wrong directory

**Solution**: Database is in `<base_dir>/.imgcomp_history/`, not in the repository root

### Issue: "No historical data showing"

**Cause**: Only first run - need at least 2 runs for trends

**Solution**: Run comparison at least twice with same images

### Issue: "Build numbers all the same"

**Cause**: Not providing unique build numbers

**Solution**: Either:
1. Let auto-generation handle it (different timestamps)
2. Provide explicit unique build numbers: `--build-number "run-001"`

---

## Next Steps

1. ✅ Database creation - **FIXED**
2. ✅ Build number auto-generation - **COMPLETE**
3. ✅ Historical data display in reports - **WORKING** (see HISTORICAL_DATA_FIX.md)
4. Optional: Add GUI control for build number input

---

**Last Updated:** December 5, 2025
