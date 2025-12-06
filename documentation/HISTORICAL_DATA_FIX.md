# Historical Data Display Fix

**Date:** December 5, 2025
**Issue:** Historical data and trend charts were not showing up in HTML reports
**Status:** ✅ **FIXED**

---

## Problem Summary

Historical data (composite scores, trend charts) was not displaying in the HTML detail reports, even when:
- `enable_history=True` was set in the configuration
- The database was being populated correctly
- Results were being enriched with historical statistics

## Root Cause Analysis

### The Issue

In [report_generator.py:141](../ImageComparisonSystem/report_generator.py#L141), the `_generate_historical_section()` method was being called with `historical_data=None`:

```python
# OLD CODE (BROKEN)
historical_section = self._generate_historical_section(result, historical_data=None)
```

This meant that even though the `ComparisonResult` objects had historical statistics attached (mean, std_dev, etc.), the **trend charts** could never be generated because:

1. The `_generate_historical_section()` method requires `historical_data` (a list of timestamp/score pairs) to generate trend charts
2. This data was never retrieved from the database during report generation
3. The `ReportGenerator` had no access to the `HistoryManager` to query historical data

### Why It Happened

The architecture separated concerns:
- **HistoryManager**: Handles database queries and enrichment of results with statistics
- **ReportGenerator**: Generates HTML reports from enriched results

However, enrichment (done in `comparator.py`) only adds aggregate statistics (mean, std_dev) to each `ComparisonResult`. It doesn't attach the full historical record needed for trend charts.

The `ReportGenerator` needed access to the `HistoryManager` to query historical data **per image** when generating reports.

---

## Solution

### Changes Made

#### 1. **Updated ReportGenerator Constructor** ([report_generator.py:67](../ImageComparisonSystem/report_generator.py#L67))

Added `history_manager` parameter to allow querying historical data:

```python
# NEW CODE
def __init__(self, config: Config, history_manager=None) -> None:
    """Initialize report generator.

    Args:
        config: Configuration object with output paths
        history_manager: Optional HistoryManager for trend chart data
    """
    self.config: Config = config
    self.history_manager = history_manager
    # ...
```

#### 2. **Updated generate_detail_report Method** ([report_generator.py:142-171](../ImageComparisonSystem/report_generator.py#L142-L171))

Added logic to retrieve historical data for each image when generating reports:

```python
# NEW CODE
# Generate historical section if available
historical_data = None
if self.history_manager and hasattr(result, 'composite_score') and result.composite_score is not None:
    try:
        # Get subdirectory for this result
        subdirectory = result.get_subdirectory(self.config.new_path)

        # Query historical data for trend charts
        history_records = self.history_manager.get_history_for_image(
            result.filename,
            subdirectory=subdirectory if subdirectory else None,
            limit=50  # Last 50 runs for trend visualization
        )

        # Format for trend chart: list of dicts with 'timestamp' and 'composite_score'
        historical_data = [
            {
                'timestamp': h['timestamp'],
                'composite_score': h['composite_score']
            }
            for h in history_records
            if h.get('composite_score') is not None
        ]

        logger.debug(f"Retrieved {len(historical_data)} historical data points for {result.filename}")
    except Exception as e:
        logger.warning(f"Failed to retrieve historical data for {result.filename}: {e}")
        historical_data = None

historical_section = self._generate_historical_section(result, historical_data=historical_data)
```

#### 3. **Updated ImageComparator Initialization** ([comparator.py:54-70](../ImageComparisonSystem/comparator.py#L54-L70))

Reordered initialization to create `HistoryManager` before `ReportGenerator`, then pass it:

```python
# NEW CODE (REORDERED)
self.config: Config = config
self.analyzer_registry: AnalyzerRegistry = AnalyzerRegistry(config)
self.processor: ImageProcessor = ImageProcessor(config)

# Initialize history manager if enabled (before ReportGenerator)
self.history_manager: Optional[HistoryManager] = None
if config.enable_history and HistoryManager is not None:
    try:
        db = Database(config.history_db_path)
        self.history_manager = HistoryManager(db, config)
        logger.info(f"History tracking enabled: {config.history_db_path}")
        # ...
    except Exception as e:
        logger.warning(f"Failed to initialize history tracking: {e}")
        self.history_manager = None

# Initialize report generator with history manager
self.report_generator: ReportGenerator = ReportGenerator(config, history_manager=self.history_manager)
```

---

## What Now Works

With this fix, the HTML detail reports now correctly display:

### 1. **Historical Statistics Section**
- Composite score with anomaly badges
- Historical mean
- Standard deviation
- Deviation from mean (σ)

### 2. **Trend Charts** (NEW - Now Working!)
- Line chart showing composite score over time
- Last 50 runs for the specific image
- Automatically generated if:
  - History is enabled
  - At least 2 historical data points exist
  - TrendChartGenerator is available (matplotlib installed)

---

## Example Output

When historical data is available, the detail report will show:

```
Historical Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Composite Score: 45.23/100 ⚠️ ANOMALY

Historical Statistics:
  Historical Mean:        32.45
  Standard Deviation:     5.12
  Deviation from Mean:    2.50σ

[Trend Chart showing composite score over last 50 runs]
```

---

## Testing the Fix

### Prerequisites

1. **Enable history tracking:**
   ```python
   config = Config(
       base_dir="path/to/images",
       enable_history=True,
       build_number="build-001"  # Required for history
   )
   ```

2. **Run multiple comparisons** to build historical data:
   ```bash
   # Run 1
   python main.py --base-dir ./images --build-number "build-001" --enable-history

   # Run 2 (same images, different build number)
   python main.py --base-dir ./images --build-number "build-002" --enable-history

   # Run 3
   python main.py --base-dir ./images --build-number "build-003" --enable-history
   ```

3. **Check the HTML reports:**
   - Open any `<image>.html` file in `reports/html/`
   - Look for the "Historical Analysis" section
   - Trend chart should appear after 2+ runs with the same image

### Verification Commands

```bash
# Check if database has data
python -c "
from ImageComparisonSystem.history import Database
db = Database('.imgcomp_history/comparison_history.db')
print(f'Total runs: {db.get_row_count(\"runs\")}')
print(f'Total results: {db.get_row_count(\"results\")}')
"

# Check if specific image has history
python -c "
from ImageComparisonSystem.history import Database, HistoryManager
from ImageComparisonSystem.config import Config

config = Config(base_dir='./images')
db = Database('.imgcomp_history/comparison_history.db')
history = HistoryManager(db, config)

history_data = history.get_history_for_image('test_image.png')
print(f'Historical records for test_image.png: {len(history_data)}')
for h in history_data[:5]:  # Show first 5
    print(f\"  Build {h['build_number']}: Score {h['composite_score']}\")
"
```

---

## Files Modified

1. **ImageComparisonSystem/report_generator.py**
   - Added `history_manager` parameter to `__init__`
   - Updated `generate_detail_report` to query historical data
   - Historical data now properly passed to `_generate_historical_section`

2. **ImageComparisonSystem/comparator.py**
   - Reordered initialization (HistoryManager before ReportGenerator)
   - Pass `history_manager` to ReportGenerator constructor

---

## Backward Compatibility

✅ **Fully backward compatible**

- If `enable_history=False`: No change in behavior, no historical section shown
- If `history_manager=None`: Historical section shows aggregate stats only (no trend chart)
- If historical data doesn't exist for an image: Shows current composite score only
- All existing functionality preserved

---

## Related Files

- **Database Schema:** `ImageComparisonSystem/history/migrations/v1_initial.sql`
- **History Manager:** `ImageComparisonSystem/history/history_manager.py`
- **Composite Metrics:** `ImageComparisonSystem/history/composite_metric.py`
- **Statistics:** `ImageComparisonSystem/history/statistics.py`
- **Trend Visualization:** `ImageComparisonSystem/visualization/trend_charts.py`

---

## Next Steps

1. ✅ Historical data display - **FIXED**
2. ⏳ Add configuration display to summary page (TODO 2)
3. ⏳ Verify repository structure documentation (TODO 3)
4. ⏳ Fix example command line pathing (TODO 4)

---

**Last Updated:** December 5, 2025
