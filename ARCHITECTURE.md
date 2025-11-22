# Image Comparison Tool - Architecture Documentation

## Overview

The Image Comparison Tool is a modular Python application designed to compare sets of images and generate comprehensive HTML reports with difference analysis. The architecture follows a layered approach with clear separation of concerns, making the codebase maintainable and extensible.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Points                             │
│  ┌──────────────────┐              ┌──────────────────┐   │
│  │    main.py       │              │   verify.py      │   │
│  │  (CLI/GUI Mode)  │              │  (Verification)  │   │
│  └──────────────────┘              └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Configuration Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  config.py - Configuration dataclass                │  │
│  │  logging_config.py - Logging setup                  │  │
│  │  dependencies.py - Dependency validation            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   UI/Interface Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ui.py - GUI interface (Tkinter)                    │  │
│  │  models.py - Data models (dataclasses)              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  Core Processing Layer                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  comparator.py - Orchestrates comparison workflow   │  │
│  │  ├─ analyzer_registry - Aggregates all analyzers    │  │
│  │  ├─ processor - Image processing utilities          │  │
│  │  └─ report_generator - Report generation            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Specialized Processing Modules                 │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │  analyzers.py    │  │  processor.py                │   │
│  │  ├─ Base class   │  │  ├─ Image loading           │   │
│  │  ├─ Pixel        │  │  ├─ Histogram equalization  │   │
│  │  ├─ SSIM         │  │  ├─ Diff generation         │   │
│  │  ├─ Color        │  │  ├─ Histogram visualization │   │
│  │  └─ Histogram    │  │  └─ Annotation              │   │
│  └──────────────────┘  └──────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  report_generator.py                                │  │
│  │  ├─ HTML report generation                          │  │
│  │  ├─ Navigation links                                │  │
│  │  └─ Summary visualization                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Output Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Diff Images  │  HTML Reports  │  Logs              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Configuration Layer (`config.py`)
**Purpose**: Centralized configuration management

- **Config dataclass**: Stores all comparison parameters
  - Directory paths (base, new, known_good, diffs, reports)
  - Tolerance thresholds (pixel_diff, ssim, color distance)
  - Visual settings (highlight color, enhancement factor)
  - Processing flags (histogram equalization)

**Key Features**:
- Automatic path conversion from strings to Path objects
- Directory validation and creation
- Property-based path access
- Configuration validation with detailed error messages

### 2. Entry Points

#### `main.py`
- Parses command-line arguments
- Initializes configuration
- Provides GUI vs CLI mode selection
- Orchestrates the comparison workflow
- Handles logging configuration

#### `verify.py`
- Installation verification script
- Tests all dependencies
- Validates core functionality
- User-facing diagnostics tool

### 3. UI Layer (`ui.py`)
**Purpose**: User interface for configuration input

- Tkinter-based GUI application
- Interactive directory selection
- Threshold adjustment controls
- Comparison execution and results display

### 4. Data Models (`models.py`)
**Purpose**: Standardized data structures

**ComparisonResult**:
```
- filename: Name of the compared images
- new_image_path: Path to new image
- known_good_path: Path to reference image
- diff_image_path: Generated diff image location
- annotated_image_path: Generated annotated image location
- metrics: Dictionary of analysis results
- percent_different: Overall difference percentage
```

### 5. Core Processing Pipeline

#### `comparator.py` (Orchestrator)
**Responsibilities**:
- Finds matching image pairs
- Coordinates the comparison workflow
- Manages result aggregation
- Handles errors and logging

**Workflow**:
1. Validates configuration
2. Cleans output directories
3. Discovers images in source directories
4. For each image pair:
   - Loads images
   - Runs all analyzers
   - Generates diffs
   - Creates annotations
   - Stores results
5. Generates summary reports
6. Opens reports in browser

#### `analyzers.py` (Analysis Engine)
**Architecture Pattern**: Registry Pattern

**Base Class**: `ImageAnalyzer`
- Abstract interface for all analyzers
- Defines `analyze()` contract

**Concrete Analyzers**:
1. **PixelDifferenceAnalyzer**
   - Calculates per-pixel differences
   - Computes percentage of changed pixels
   - Mean Absolute Error (MAE)
   - Maximum difference values

2. **StructuralSimilarityAnalyzer**
   - SSIM metric calculation
   - Grayscale conversion
   - Structural similarity mapping
   - Human-readable descriptions

3. **ColorDifferenceAnalyzer**
   - Per-channel analysis
   - Color distance calculations
   - Grayscale detection

4. **HistogramAnalyzer**
   - Histogram comparison
   - Chi-squared statistic
   - Distribution analysis

**AnalyzerRegistry**:
- Aggregates all analyzers
- Provides unified `analyze_all()` interface
- Returns consolidated metrics

#### `processor.py` (Image Processing)
**Capabilities**:
- Image loading and format conversion
- Size normalization
- Histogram equalization
- Difference map generation
- Annotation with bounding boxes
- Histogram visualization
- Base64 encoding for HTML embedding

**Key Methods**:
- `load_images()`: Safe image loading with format handling
- `equalize_histogram()`: Tonal normalization
- `generate_diff()`: Difference highlighting
- `generate_annotated_image()`: Visual annotations
- `generate_histogram_image()`: Comparison visualization

#### `report_generator.py` (Report Creation)
**Features**:
- HTML report generation
- Navigation between reports
- Embedded image visualization
- Metrics display
- Summary page creation
- Statistics visualization

**Report Components**:
- Detailed comparison page per image pair
- Summary page with all results
- Navigation links between reports
- Histogram comparisons
- Diff visualization

### 6. Supporting Modules

#### `dependencies.py`
- Checks for required packages
- Provides installation instructions
- Supports both pip and conda
- Offline installation support

#### `logging_config.py`
- Centralized logging setup
- Multiple log level support
- Console and file output
- Consistent formatting

## Data Flow

### Comparison Workflow

```
User Input (CLI or GUI)
        ↓
    Config Creation
        ↓
    Input Validation
        ↓
    Image Discovery
        ↓
    ┌─────────────────────────────────┐
    │ For Each Image Pair             │
    ├─────────────────────────────────┤
    │ 1. Load Images                  │
    │ 2. Normalize Sizes              │
    │ 3. Apply Preprocessing          │
    │ 4. Run All Analyzers            │
    │    ├─ Pixel Analysis            │
    │    ├─ SSIM Analysis             │
    │    ├─ Color Analysis            │
    │    └─ Histogram Analysis        │
    │ 5. Generate Diff Image          │
    │ 6. Generate Annotations         │
    │ 7. Store Results                │
    └─────────────────────────────────┘
        ↓
    Result Aggregation
        ↓
    Report Generation
        ↓
    Summary Creation
        ↓
    Browser Display
```

## Design Patterns Used

### 1. **Registry Pattern** (`analyzers.py`)
- Dynamic registration of analyzers
- Extensible without modifying core code
- Easy to add new comparison metrics

### 2. **Dataclass Pattern** (`config.py`, `models.py`)
- Immutable configuration objects
- Built-in validation support
- Type safety

### 3. **Strategy Pattern** (Analyzers)
- Different analysis strategies encapsulated
- Interchangeable implementations
- Unified interface

### 4. **Composite Pattern** (`comparator.py`)
- Complex workflow broken into steps
- Orchestration of multiple components
- Error handling at each stage

### 5. **Singleton Pattern** (Logger)
- Single logger instance across application
- Consistent logging format
- Centralized configuration

## Error Handling Strategy

### Error Categories

1. **Configuration Errors** (Early detection)
   - Missing directories
   - Invalid paths
   - Invalid parameters
   
2. **Dependency Errors** (Pre-flight checks)
   - Missing packages
   - Version conflicts
   
3. **Processing Errors** (Per-image handling)
   - Corrupted images
   - Unsupported formats
   - Processing failures
   
4. **Output Errors** (Report generation)
   - Write failures
   - Browser launch issues

### Error Handling Approach

- **Early Validation**: Check configuration immediately
- **Graceful Degradation**: Continue processing on non-fatal errors
- **Detailed Logging**: Log all errors with context
- **User Feedback**: Display actionable error messages
- **Specific Exception Types**: Catch known exceptions, not bare `except:`

## Extension Points

### Adding a New Analyzer

1. Create class inheriting from `ImageAnalyzer`
2. Implement `analyze()` method
3. Implement `name` property
4. Register in `AnalyzerRegistry`

**Example**:
```python
class EdgeDetectionAnalyzer(ImageAnalyzer):
    @property
    def name(self) -> str:
        return "Edge Detection"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> Dict[str, Any]:
        # Implementation
        pass
```

### Adding a New Report Format

1. Create method in `ReportGenerator`
2. Follow HTML generation pattern
3. Ensure path management
4. Add to comparison workflow

## Performance Considerations

1. **Image Loading**: Lazy loading where possible
2. **Memory**: Process large images in tiles if needed
3. **Caching**: Cache histogram calculations
4. **Parallelization**: Future enhancement for multiple image processing
5. **Report Generation**: Batch HTML generation for efficiency

## Testing Strategy

### Test Organization
- `tests/test_*.py`: Unit tests for modules
- `tests/integration/`: Integration tests
- `tests/fixtures/`: Test data and fixtures

### Test Coverage
- Configuration validation
- Image loading and processing
- Analyzer accuracy
- Report generation
- Error handling

## Future Enhancements

1. **Parallelization**: Process multiple image pairs concurrently
2. **Performance**: Add image caching for repeated comparisons
3. **Machine Learning**: Add ML-based anomaly detection
4. **Database**: Store results in database for historical tracking
5. **API**: REST API for programmatic access
6. **Batch Processing**: Support for comparing multiple directories
7. **Custom Metrics**: Plugin system for user-defined analyzers

## Module Dependencies

```
main.py
├── config.py
├── logging_config.py
├── dependencies.py
├── ui.py
└── comparator.py
    ├── config.py
    ├── analyzers.py
    │   └── (numpy, PIL, skimage, cv2)
    ├── processor.py
    │   └── (numpy, PIL, cv2, matplotlib)
    ├── report_generator.py
    │   └── config.py
    └── models.py

verify.py
├── logging_config.py
├── dependencies.py
├── config.py
├── ui.py
├── analyzers.py
└── processor.py
```

## Configuration Management

### Configuration Files
- Command-line arguments (primary)
- GUI input (secondary)
- Default values in `Config` dataclass

### Configuration Hierarchy
1. Default values in Config
2. Command-line overrides
3. GUI modifications

## Logging Architecture

### Log Levels
- **DEBUG**: Detailed operation information
- **INFO**: Successful operations and progress
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures with context
- **CRITICAL**: System-level failures

### Log Output
- Console: Real-time feedback
- File: Persistent record (optional)
- Structured: Consistent format across app

## Security Considerations

1. **Path Validation**: All paths validated against traversal attacks
2. **File Operations**: Safe file handling with error checking
3. **Input Validation**: All user inputs validated
4. **Dependency Checking**: Pre-flight dependency verification
