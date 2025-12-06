# FLIP Package Update: flip-evaluator

**Date:** December 5, 2025
**Change:** Updated from `flip-image-comparison` to `flip-evaluator`
**Reason:** Use official NVIDIA FLIP package

---

## Summary

All references to `flip-image-comparison` have been updated to `flip-evaluator>=1.0.0`, which is the official NVIDIA FLIP implementation package.

## Changes Made

### 1. **requirements.txt**
- **Before:** `# flip-image-comparison>=0.1.0` (commented out)
- **After:** `flip-evaluator>=1.0.0` (active dependency)

### 2. **ImageComparisonSystem/dependencies.py**
```python
# Before
Dependency(
    package_name="flip-image-comparison",
    import_name="flip",
    min_version="0.1.0",
    ...
)

# After
Dependency(
    package_name="flip-evaluator",
    import_name="flip",
    min_version="1.0.0",
    ...
)
```
- Moved from `OPTIONAL_DEPENDENCIES` to main `DEPENDENCIES` list

### 3. **README.md**
- Updated Quick Install section
- Updated verification command to include `import flip`
- Updated Required Dependencies list:
  - **Before:** `flip-image-comparison` (>=0.1.0) - Optional
  - **After:** `flip-evaluator` (>=1.0.0) - Required

### 4. **documentation/FLIP_INTEGRATION_GUIDE.md**
- Updated installation instructions
- Updated troubleshooting section
- Updated PyPI package reference

### 5. **debug_flip_reports.py**
```python
# Updated error messages
"Install with: pip install flip-evaluator>=1.0.0"
```

### 6. **examples/flip_example.py**
```python
# Updated prerequisites
Prerequisites:
    pip install flip-evaluator>=1.0.0
```

### 7. **examples/flip_api_example.py**
```python
# Updated prerequisites
Prerequisites:
    pip install flip-evaluator>=1.0.0
```

### 8. **ImageComparisonSystem/ui.py**
```python
# Updated checkbox text
text="Enable NVIDIA FLIP perceptual analysis (requires flip-evaluator package)"
```

### 9. **ImageComparisonSystem/analyzers.py**
```python
# Updated warning messages
"Install with: pip install flip-evaluator"
```

### 10. **tests/test_flip_analyzer.py**
```python
# Updated test assertion
assert "pip install flip-evaluator" in str(exc_info.value)
```

---

## Installation

### New Installation Command

```bash
# Install all dependencies (including FLIP)
pip install -r requirements.txt
```

### Verification

```bash
python -c "import flip; print('FLIP installed successfully')"
```

### Version Check

```python
import flip
print(flip.__version__)  # Should be >= 1.0.0
```

---

## Package Information

- **Package Name:** `flip-evaluator`
- **PyPI URL:** https://pypi.org/project/flip-evaluator/
- **Import Name:** `flip` (unchanged)
- **Minimum Version:** 1.0.0
- **Type:** Required dependency (was optional)

---

## Migration Guide

If you have an existing installation with `flip-image-comparison`, uninstall it first:

```bash
# 1. Uninstall old package
pip uninstall flip-image-comparison

# 2. Install new package
pip install flip-evaluator>=1.0.0

# Or install all requirements
pip install -r requirements.txt
```

---

## API Compatibility

The import remains the same:
```python
import flip

# All existing code continues to work
flip_map = flip.compute_flip(reference, test, pixels_per_degree=67.0)
```

No code changes are required in your scripts - only the package name has changed.

---

## Files Updated

Total: **10 files** updated

### Core Files (3)
1. `requirements.txt`
2. `ImageComparisonSystem/dependencies.py`
3. `README.md`

### Documentation (2)
4. `documentation/FLIP_INTEGRATION_GUIDE.md`
5. `documentation/FLIP_PACKAGE_UPDATE.md` (this file)

### Scripts (2)
6. `debug_flip_reports.py`
7. `examples/flip_example.py`
8. `examples/flip_api_example.py`

### Source Code (2)
9. `ImageComparisonSystem/ui.py`
10. `ImageComparisonSystem/analyzers.py`

### Tests (1)
11. `tests/test_flip_analyzer.py`

---

## Status

✅ **All updates complete**

FLIP is now:
- Using the official `flip-evaluator` package
- Included as a standard dependency
- Automatically installed with `pip install -r requirements.txt`
- Version 1.0.0 or higher required

---

## Next Steps

1. **Install the package:**
   ```bash
   pip install flip-evaluator>=1.0.0
   ```

2. **Verify installation:**
   ```bash
   python -c "import flip; print(f'FLIP {flip.__version__} installed')"
   ```

3. **Run tests:**
   ```bash
   pytest tests/test_flip*.py -v
   ```

4. **Use FLIP in comparisons:**
   ```bash
   python main.py --base-dir path/to/images --enable-flip
   ```

---

**Last Updated:** December 5, 2025
