# Image Comparison Tool - Repository Structure

**Last Updated:** December 5, 2025

This document describes the current repository structure for the ImageComparisonTool project.

---

## Repository Overview

```
ImageComparisonTool/
├── ImageComparisonSystem/          # Main package
│   ├── annotations/                # Annotation and export features
│   ├── history/                    # Historical tracking system
│   ├── visualization/              # Chart generation and visualization
│   └── *.py                        # Core modules
├── tests/                          # Test suite
│   └── integration/                # Integration tests
├── examples/                       # Example scripts
├── documentation/                  # Documentation files
├── ExampleCommandLines/            # Test scripts and examples
├── Planning/                       # Planning documents
├── .github/                        # GitHub templates and workflows
└── [Configuration Files]           # setup.py, requirements.txt, etc.
```

---

## Directory Structure

### 📦 **ImageComparisonSystem/** - Main Package

The core application package containing all functional modules.

#### Core Modules

| File | Purpose |
|------|---------|
| `__init__.py` | Package initialization, exports public API |
| `main.py` | Entry point for CLI |
| `ui.py` | Tkinter GUI interface with theme support |
| `config.py` | Configuration management and validation |
| `comparator.py` | Orchestrates comparison workflow |
| `processor.py` | Image loading and processing utilities |
| `analyzers.py` | Modular image analysis (Pixel, SSIM, Histogram, FLIP) |
| `models.py` | Data models (ComparisonResult, etc.) |
| `report_generator.py` | HTML report generation with charts |
| `markdown_exporter.py` | Markdown summary export for CI/CD |
| `dependencies.py` | Dependency validation and installation checks |
| `logging_config.py` | Centralized logging configuration |
| `verify.py` | Installation verification script |
| `check_script.py` | Quick system health check |

#### 📊 **history/** Subdirectory

Historical metrics tracking and statistical analysis.

| File | Purpose |
|------|---------|
| `__init__.py` | Exports Database, HistoryManager, RetentionPolicy |
| `database.py` | SQLite database management and migrations |
| `history_manager.py` | High-level history tracking interface |
| `composite_metric.py` | Composite score calculation from multiple metrics |
| `statistics.py` | Statistical analysis and anomaly detection |
| `retention.py` | Data retention policies and cleanup |
| `migrations/v1_initial.sql` | Database schema v1 |
| `migrations/v2_add_flip.sql` | FLIP metrics schema addition |

#### 📝 **annotations/** Subdirectory

Annotation management and export formats.

| File | Purpose |
|------|---------|
| `__init__.py` | Exports AnnotationManager |
| `annotation_manager.py` | Annotation tracking and persistence |
| `export_formats.py` | Export to COCO, YOLO, CSV formats |

#### 📈 **visualization/** Subdirectory

Trend charts and data visualization.

| File | Purpose |
|------|---------|
| `__init__.py` | Exports TrendChartGenerator |
| `trend_charts.py` | matplotlib-based trend chart generation |

---

### 🧪 **tests/** - Test Suite

Comprehensive test coverage using pytest.

#### Test Files

| File | Tests |
|------|-------|
| `conftest.py` | pytest fixtures and configuration |
| `test_config.py` | Configuration validation |
| `test_comparator.py` | Comparison workflow |
| `test_analyzers.py` | Image analysis modules |
| `test_processor.py` | Image processing |
| `test_models.py` | Data model validation |
| `test_report_generator.py` | HTML report generation |
| `test_markdown_exporter.py` | Markdown export |
| `test_dependencies.py` | Dependency checking |
| `test_flip_analyzer.py` | FLIP integration |
| `test_flip_integration.py` | End-to-end FLIP tests |
| `test_database.py` | Database operations |
| `test_history_manager.py` | History tracking |
| `test_composite_metric.py` | Composite score calculation |
| `test_statistics.py` | Statistical analysis |
| `test_retention.py` | Data retention policies |
| `test_annotation_manager.py` | Annotation management |
| `test_export_formats.py` | Export format validation |
| `test_config_history.py` | Configuration history tracking |
| `test_histogram_config.py` | Histogram configuration |

#### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing (`tests/integration/`)
- **Test Coverage**: Configured for 80%+ coverage (see `pytest.ini`)

---

### 📚 **documentation/** - Documentation

Comprehensive guides and technical documentation.

#### Main Documentation Files

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | System architecture overview |
| `SETUP_GUIDE.md` | Installation and setup instructions |
| `TESTING.md` | Test suite documentation |
| `cheatsheet.md` | Quick reference commands |
| `repo_structure.md` | Legacy structure document (outdated) |
| `REPOSITORY_STRUCTURE.md` | **This file** - current structure |

#### Feature Documentation

| File | Purpose |
|------|---------|
| `FLIP_INTEGRATION_GUIDE.md` | NVIDIA FLIP integration guide |
| `FLIP_INTEGRATION_COMPLETE.md` | FLIP implementation summary |
| `FLIP_PACKAGE_UPDATE.md` | flip-evaluator migration guide |
| `HISTORICAL_TRACKING_COMPLETE.md` | Historical tracking feature summary |
| `HISTORICAL_DATA_FIX.md` | Historical data display fix documentation |
| `MARKDOWN_EXPORT.md` | Markdown export feature guide |
| `TODO_RESOLUTION.md` | TODO item tracking |

#### Implementation Documentation

| File | Purpose |
|------|---------|
| `IMPLEMENTATION_SUMMARY.md` | Phase-based implementation summary |
| `PYPI_PUBLISHING.md` | PyPI publishing guide |
| `PYPI_PUBLISHING_QUICKSTART.md` | Quick PyPI setup |
| `PYPI_READY_FOR_PUBLICATION.md` | Publication readiness checklist |
| `PYPI_FILES_SUMMARY.md` | PyPI package file descriptions |

---

### 💡 **examples/** - Example Scripts

Demonstration scripts for common use cases.

| File | Purpose |
|------|---------|
| `flip_example.py` | FLIP usage examples (7 scenarios) |
| `flip_api_example.py` | Programmatic FLIP API examples |
| `reports/summary.md` | Example markdown export output |

---

### 🔧 **ExampleCommandLines/** - Test Scripts

Manual test scripts and examples.

| File | Purpose |
|------|---------|
| `test_historical_tracking_manual.py` | Manual historical tracking test |
| `test_history_simple.py` | Simple history test |
| `TEST_FILES_README.md` | Test file documentation |
| `TEST_ORGANIZATION.md` | Test organization guide |

---

### 📋 **Planning/** - Planning Documents

Design and planning documentation.

| File | Purpose |
|------|---------|
| `NVIDIA_FLIP_Integration_Plan.md` | FLIP integration planning |

---

### 🔧 **Root Directory Files**

#### Configuration Files

| File | Purpose |
|------|---------|
| `setup.py` | Package installation configuration (PyPI) |
| `requirements.txt` | Python package dependencies |
| `requirements.py` | Dependency list generator (deprecated) |
| `MANIFEST.in` | Package distribution manifest |
| `pytest.ini` | pytest configuration |
| `.gitignore` | Git ignore patterns |

#### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `quickstart.md` | Quick start guide |
| `CHANGELOG.md` | Version history and changes |
| `contributing.md` | Contribution guidelines |
| `license.md` | MIT License |

#### Debug and Diagnostic Scripts

| File | Purpose |
|------|---------|
| `debug_flip_reports.py` | FLIP report debugging tool |
| `diagnose_tests.py` | Test suite diagnostics |
| `test_database_manual.py` | Manual database testing |
| `test_historical_tracking_manual.py` | Manual history testing |
| `test_history_simple.py` | Simple history test |
| `test_phase6_models.py` | Phase 6 model testing |
| `test_phases_1_to_5.py` | Phase 1-5 testing |

#### Generated/Status Files

| File | Purpose |
|------|---------|
| `BUGFIX_SUMMARY.md` | Bug fix documentation |
| `CONFIG_FIX.md` | Configuration fix notes |
| `GUI_UPDATES.md` | GUI update notes |
| `HISTORICAL_TRACKING_PROGRESS.md` | Historical tracking progress |
| `IMPORT_FIX.md` | Import fix documentation |
| `PARALLEL_PROCESSING_GUI.md` | Parallel processing GUI notes |
| `PHASE_12_SUMMARY.md` | Phase 12 summary |
| `README_UPDATED.md` | README update notes |
| `SETUP_GUIDE.md` | Setup guide (root level) |
| `TEST_FIXES_COMPLETE.md` | Test fix summary |
| `TEST_FIX_SUMMARY.md` | Test fix details |

---

### 🐙 **.github/** - GitHub Configuration

GitHub-specific configuration and templates.

#### Issue Templates

| File | Purpose |
|------|---------|
| `ISSUE_TEMPLATE/bug_report.md` | Bug report template |
| `ISSUE_TEMPLATE/feature_request.md` | Feature request template |
| `ISSUE_TEMPLATE/custom.md` | Custom issue template |
| `issue_template.md` | Legacy issue template |

#### Pull Request Templates

| File | Purpose |
|------|---------|
| `pr_template.md` | Pull request template |

#### Other Templates

| File | Purpose |
|------|---------|
| `feature_template.md` | Feature planning template |

---

## Key File Count

| Category | Count |
|----------|-------|
| **Core Modules** | 14 files |
| **History System** | 6 files + migrations |
| **Annotations** | 2 files |
| **Visualization** | 1 file |
| **Tests** | 20+ test files |
| **Documentation** | 20+ documentation files |
| **Examples** | 2 scripts |
| **Configuration** | 6 root config files |
| **Total Python Files** | 50+ files |

---

## Generated Directories (Not in Git)

These directories are created during usage and excluded from version control:

```
.imgcomp_history/               # Historical database storage
├── comparison_history.db       # SQLite database
└── backups/                    # Database backups

reports/                        # Generated reports
├── diffs/                      # Difference images
│   ├── diff_*.png             # Standard diff images
│   ├── annotated_*.png        # Annotated images
│   └── flip_heatmap_*.png     # FLIP heatmap visualizations
└── html/                       # HTML reports
    ├── summary.html           # Main summary page
    ├── subdir_*.html          # Subdirectory index pages
    ├── *.html                 # Individual comparison reports
    └── results.json           # JSON export

__pycache__/                    # Python bytecode cache
.pytest_cache/                  # pytest cache
*.egg-info/                     # Package metadata
```

---

## Feature Map

### Core Features → Files

| Feature | Primary Files |
|---------|--------------|
| **Image Comparison** | `comparator.py`, `processor.py`, `analyzers.py` |
| **NVIDIA FLIP Analysis** | `analyzers.py` (FLIPAnalyzer class) |
| **HTML Reports** | `report_generator.py` |
| **Markdown Export** | `markdown_exporter.py` |
| **Historical Tracking** | `history/` directory (all files) |
| **Trend Visualization** | `visualization/trend_charts.py` |
| **Annotations** | `annotations/` directory |
| **GUI Interface** | `ui.py` |
| **CLI Interface** | `main.py` |
| **Configuration** | `config.py` |
| **Dependency Checking** | `dependencies.py` |
| **Testing** | `tests/` directory |

---

## Package Dependencies

See `requirements.txt` for full list. Key dependencies:

- **Image Processing**: numpy, opencv-python, Pillow, scikit-image
- **Analysis**: scipy
- **FLIP**: flip-evaluator (>=1.0.0)
- **GUI**: tkinter (included with Python)
- **Visualization**: matplotlib
- **Testing**: pytest, pytest-cov

---

## Migration Notes

### From Legacy Structure

The repository has evolved from a flat structure to a package-based structure:

**Old (Legacy)**:
```
/
├── main.py
├── config.py
├── ui.py
├── comparator.py
└── ...
```

**New (Current)**:
```
/
└── ImageComparisonSystem/
    ├── main.py
    ├── config.py
    ├── ui.py
    ├── comparator.py
    ├── history/
    ├── annotations/
    ├── visualization/
    └── ...
```

---

## Maintenance Guidelines

### Adding New Features

1. **New analyzer**: Add class to `analyzers.py`, register in `AnalyzerRegistry`
2. **New metric**: Update `models.py`, add to `composite_metric.py` weights
3. **New export format**: Add to `annotations/export_formats.py`
4. **New visualization**: Add to `visualization/` directory
5. **Database schema changes**: Create new migration file in `history/migrations/`

### Documentation Updates

- Update this file when adding new modules or directories
- Update `ARCHITECTURE.md` for architectural changes
- Update `FLIP_INTEGRATION_GUIDE.md` for FLIP-related changes
- Create feature-specific documentation in `documentation/`

### Testing Requirements

- All new features must have unit tests in `tests/`
- Integration tests for end-to-end workflows
- Maintain 80%+ test coverage (enforced in `pytest.ini`)

---

## Version Control

### Branches

- `main`: Stable release branch
- `develop`: Development branch (if used)
- Feature branches: `feature/feature-name`
- Bug fixes: `bugfix/issue-description`

### Tags

- Release tags: `v1.0.0`, `v1.1.0`, etc.
- Follow semantic versioning

---

## Additional Resources

- **Main README**: See `README.md` for user-facing documentation
- **API Documentation**: See `ARCHITECTURE.md`
- **Setup Instructions**: See `documentation/SETUP_GUIDE.md`
- **Testing Guide**: See `documentation/TESTING.md`
- **FLIP Guide**: See `documentation/FLIP_INTEGRATION_GUIDE.md`

---

**Last Updated:** December 5, 2025
**Repository**: https://github.com/sjbudlong/ImageComparisonTool
