# GUI Updates - Historical Tracking Integration

## Summary
Added comprehensive historical metrics tracking configuration to the GUI by expanding the interface horizontally with a dedicated right panel.

## Changes Made

### 1. Window Size Expansion
- **Before:** 800x1000 pixels
- **After:** 1400x1000 pixels (expanded 600px to the right)
- Layout: Two-column design (left: existing settings, right: historical tracking)

### 2. New Right Panel: "Historical Metrics Tracking"

The right panel includes three sections:

#### Section 1: Basic Historical Tracking
- ✅ **Enable historical metrics tracking** (checkbox, default: ON)
  - Enables/disables all history features
  - Maps to: `--enable-history` / `--no-history`

- **Build Number/ID** (text input, optional)
  - Identifier for this comparison run
  - Maps to: `--build-number`

- **History DB Path** (text input, optional)
  - Custom database location
  - Default: `<base-dir>/.imgcomp_history/comparison_history.db`
  - Maps to: `--history-db`

#### Section 2: Anomaly Detection
- **Anomaly Threshold (σ):** (numeric input, default: 2.0)
  - Standard deviations from historical mean to flag anomalies
  - Maps to: `anomaly_threshold` in Config
  - Range: Typically 1.5-3.0

#### Section 3: Data Retention (Cleanup)
- ✅ **Keep all historical runs** (checkbox, default: ON)
  - When checked: All runs are preserved
  - When unchecked: Enables retention limits below

- **Max Runs to Keep** (numeric input, disabled by default)
  - Maximum number of historical runs to retain
  - Maps to: `--max-runs` (cleanup command)

- **Max Age (days)** (numeric input, disabled by default)
  - Maximum age in days for runs to keep
  - Maps to: `--max-age-days` (cleanup command)

- ✅ **Always keep annotated results** (checkbox, default: ON, disabled by default)
  - Protects runs with annotations from cleanup

- ✅ **Always keep anomalous results** (checkbox, default: ON, disabled by default)
  - Protects runs with detected anomalies from cleanup

### 3. Interactive Field Management

#### Toggle Behavior 1: Enable History
When "Enable historical metrics tracking" is unchecked:
- Build Number field → disabled
- History DB Path field → disabled
- Anomaly Threshold field → disabled

#### Toggle Behavior 2: Retention Policy
When "Keep all historical runs" is checked (default):
- Max Runs to Keep → disabled
- Max Age (days) → disabled
- Keep annotated checkbox → disabled
- Keep anomalies checkbox → disabled

When unchecked:
- All retention fields → enabled for configuration

### 4. Config Integration

The GUI now passes the following additional parameters to `Config`:

```python
Config(
    # ... existing parameters ...

    # Historical tracking settings
    enable_history=bool,           # True/False
    build_number=str | None,       # Optional identifier
    history_db_path=Path | None,   # Optional custom DB path
    anomaly_threshold=float,       # Default: 2.0

    # Retention policy settings
    retention_keep_all=bool,           # True/False
    retention_max_runs=int | None,     # Optional limit
    retention_max_age_days=int | None, # Optional age limit
    retention_keep_annotated=bool,     # True/False
    retention_keep_anomalies=bool,     # True/False
)
```

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│             Image Comparison Configuration                          │
├────────────────────────────┬────────────────────────────────────────┤
│                            │                                        │
│  LEFT PANEL (Existing)     │  RIGHT PANEL (New)                    │
│  ───────────────────       │  ─────────────────                    │
│                            │                                        │
│  • Base Directory          │  Historical Metrics Tracking           │
│  • New Images Dir          │  ═══════════════════════════           │
│  • Known Good Dir          │                                        │
│  • Diff Output Dir         │  ☑ Enable historical metrics tracking │
│  • HTML Reports Dir        │  Build Number/ID: [          ]        │
│                            │  History DB Path: [          ]        │
│  Tolerances & Thresholds   │                                        │
│  ════════════════════       │  Anomaly Detection                    │
│  • Pixel Diff Threshold    │  ─────────────────                    │
│  • Min Pixel Change        │  Anomaly Threshold (σ): [ 2.0  ]     │
│  • SSIM Threshold          │                                        │
│  • Color Distance          │  Data Retention (Cleanup)             │
│  • Min Bounding Box Area   │  ─────────────────────────            │
│                            │  ☑ Keep all historical runs           │
│  Visual Settings           │  Max Runs to Keep: [     ] (disabled) │
│  ════════════               │  Max Age (days):   [     ] (disabled) │
│  • Histogram Equalization  │  ☑ Keep annotated  (disabled)         │
│  • Highlight Color         │  ☑ Keep anomalies  (disabled)         │
│  • Diff Enhancement        │                                        │
│                            │  Info: Historical tracking stores     │
│  Histogram Visualization   │  metrics in SQLite for trend analysis │
│  ════════════════════       │  and anomaly detection.               │
│  • Bins, Width, Height     │                                        │
│  • Alpha, Line Width       │                                        │
│  • Show Grayscale/RGB      │                                        │
│                            │                                        │
└────────────────────────────┴────────────────────────────────────────┘
│              [Start Comparison]  [Cancel]                           │
└─────────────────────────────────────────────────────────────────────┘
```

## User Experience Improvements

### 1. **Logical Grouping**
- Comparison settings on the left
- Advanced historical features on the right
- Clear visual separation with bordered frame

### 2. **Smart Defaults**
- History enabled by default (most users want this)
- Keep all runs by default (safe option)
- 2.0σ anomaly threshold (95% confidence interval)
- Retention protections enabled (preserve important data)

### 3. **Progressive Disclosure**
- Retention fields hidden until user opts into cleanup
- Historical fields disabled when history is turned off
- Prevents accidental data loss

### 4. **Help Text**
- Inline hints for technical parameters
- Informative descriptions at section bottom
- σ symbol with explanation "(standard deviations)"

## Files Modified

### [ui.py](ImageComparisonSystem/ui.py)

**Changes:**
1. Line 29: Window geometry `"800x1000"` → `"1400x1000"`
2. Lines 34-53: Restructured layout with container frame and two panels
3. Lines 350-508: New `_create_history_widgets()` method
4. Lines 510-524: New toggle methods for interactive fields
5. Lines 594-633: Updated `_on_start()` to parse and pass historical settings to Config

**Lines Added:** ~170 new lines
**Net Impact:** Minimal change to existing code (mostly layout restructuring)

## Command-Line Equivalents

The GUI now provides access to these CLI flags:

| GUI Field | CLI Flag | Default |
|-----------|----------|---------|
| Enable historical tracking | `--enable-history` / `--no-history` | enabled |
| Build Number/ID | `--build-number TEXT` | None |
| History DB Path | `--history-db PATH` | auto |
| Anomaly Threshold | (Config only) | 2.0 |
| Keep all runs | (Config only) | True |
| Max Runs to Keep | `--max-runs N` (cleanup) | None |
| Max Age (days) | `--max-age-days N` (cleanup) | None |

**Note:** Cleanup actions (`--cleanup-history`, `--history-stats`, `--export-annotations`) remain CLI-only as they are administrative operations.

## Testing Recommendations

1. **Launch GUI**: Verify window opens at 1400x1000
2. **Toggle History**: Uncheck "Enable" and verify fields disable
3. **Toggle Retention**: Uncheck "Keep all runs" and verify retention fields enable
4. **Create Config**: Enter values and click "Start Comparison"
5. **Verify Config**: Check that Config object contains all historical parameters

## Backward Compatibility

✅ **Fully compatible** - All historical parameters are optional in Config
- Existing configs without history settings work unchanged
- Default values applied when GUI fields are empty
- CLI mode unaffected by GUI changes

---

**Updated:** December 3, 2025
**Feature:** Historical Metrics Tracking GUI Integration
**Status:** Complete ✓
