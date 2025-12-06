# Testing & Logging Guide

## Overview

This document describes the testing infrastructure and logging system for the Image Comparison Tool.

### Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=ImageComparisonSystem --cov-report=html

# Run only unit tests
pytest tests/ -m unit

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run with debug logging
pytest tests/ --log-level=DEBUG
```

---

## Directory Structure

### Tests Organization

```
tests/
├── __init__.py                    # Test package marker
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_config.py                 # Config validation tests
├── test_models.py                 # ComparisonResult serialization tests
├── test_processor.py              # Image processing tests
├── test_dependencies.py           # Dependency checker tests
├── fixtures/                      # Test images and data
│   ├── sample_new.png            # (Created at runtime if needed)
│   ├── sample_known_good.png     # (Created at runtime if needed)
│   └── sample_different.png      # (Created at runtime if needed)
└── integration/                   # Integration tests
    ├── __init__.py
    └── test_end_to_end.py       # (To be added) Full workflow tests
```

**Note:** Test batch files (test_*.bat, test_*.sh) are in the repository root, separate from pytest tests. They are manual/demonstration scripts.

### Separation Rationale

- **Pytest tests** (`tests/` directory): Automated unit tests, run by CI/CD
- **Test batch files** (root directory): Manual demonstration scripts for testing different CLI configurations

This separation keeps:
- Automated tests isolated and reproducible
- Manual test scripts accessible for quick demonstration
- Clean separation of concerns

---

## Logging System

### Configuration

Logging is configured in `ImageComparisonSystem/logging_config.py`:

```python
from logging_config import setup_logging, get_logger, LOG_LEVELS
import logging

# Initialize logging (called in main.py)
logger = setup_logging(
    level=logging.INFO,           # Console log level
    log_file=Path("app.log"),     # Optional file output
    console=True                  # Include console output
)

# Get logger in any module
logger = get_logger()
```

### Log Levels

- **DEBUG**: Detailed information for developers (default in file)
- **INFO**: General informational messages (default for console)
- **WARNING**: Warning messages, potential issues
- **ERROR**: Error messages, failures in functionality
- **CRITICAL**: Critical errors, application-level failures

### Using Logging in Code

#### Basic Usage

```python
import logging
logger = logging.getLogger("ImageComparison")

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Something unexpected happened")
logger.error("An error occurred")
logger.error("Error details:", exc_info=True)  # Include traceback
logger.critical("Critical failure")
```

#### Examples in Codebase

```python
# comparator.py
logger.info(f"Found {total} images to compare")
logger.warning(f"No matching known good image found for {filename}")
logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)

# main.py
logger.info("Starting image comparison...")
logger.critical(f"Critical dependency missing: {e}")
```

### Command-Line Options

```bash
# Set logging level
python main.py --base-dir /path --log-level debug

# Log to file
python main.py --base-dir /path --log-file app.log

# Combine both
python main.py --base-dir /path --log-level debug --log-file app.log

# Log levels: debug, info, warning, error, critical
```

### Log Output Format

**Console Output:**
```
[INFO    ] ImageComparison - Starting image comparison...
[DEBUG   ] ImageComparison - Cleaned diffs directory
[WARNING ] ImageComparison - No matching known good image found for test.png
[ERROR   ] ImageComparison - Error processing test.png: division by zero
```

**File Output (with timestamps):**
```
2025-11-21 10:30:45 - ImageComparison - INFO     - main:245 - Starting image comparison...
2025-11-21 10:30:46 - ImageComparison - DEBUG    - comparator:42 - Cleaned diffs directory
2025-11-21 10:30:47 - ImageComparison - WARNING  - comparator:87 - No matching known good image found
```

### Log Files

- Stored in project root by default (e.g., `app.log`)
- Rotates automatically at 10 MB, keeping last 5 backups
- File logging level is always DEBUG (more verbose than console)
- Console logging level is configurable via `--log-level`

---

## Test Architecture

### Pytest Fixtures

Fixtures are defined in `conftest.py` and automatically available to all tests:

```python
@pytest.fixture
def temp_image_dir(tmp_path):
    """Create temporary directory with test images."""
    # Used in tests that need a working directory
    return tmp_path

@pytest.fixture
def simple_test_image():
    """Create a simple test image."""
    # Red 100x100 image for testing
    return img

@pytest.fixture
def valid_config(temp_image_dir, new_and_known_good_dirs):
    """Create a valid Config with actual directories."""
    # Ready-to-use config for integration tests
    return config
```

### Test Markers

Tests are organized with markers for selective execution:

```python
@pytest.mark.unit
class TestConfig:
    """Unit tests - fast, isolated"""
    pass

@pytest.mark.integration
class TestComparatorIntegration:
    """Integration tests - slower, require dependencies"""
    pass

@pytest.mark.slow
def test_large_image_processing():
    """Marked as slow for filtering"""
    pass
```

**Running specific markers:**
```bash
# Run only unit tests
pytest tests/ -m unit

# Run integration tests
pytest tests/ -m integration

# Run all except slow tests
pytest tests/ -m "not slow"
```

### Test Modules

#### `test_config.py`
Tests for `Config` dataclass:
- Path handling and normalization
- Default values
- Configuration validation
- Directory creation

#### `test_models.py`
Tests for `ComparisonResult` dataclass:
- Object creation
- Dictionary serialization
- Path conversion (Path → string)
- Complex metrics preservation

#### `test_processor.py`
Tests for `ImageProcessor` functionality:
- Histogram equalization (grayscale and color)
- Histogram image generation
- Base64 encoding
- Different image formats

#### `test_dependencies.py`
Tests for `DependencyChecker`:
- Dependency detection
- Version checking
- Critical dependencies validation

---

## Running Tests

### Basic Test Runs

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with short summary
pytest tests/ --tb=short

# Run with detailed traceback
pytest tests/ --tb=long

# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n 4  # Use 4 processors
```

### Coverage Reports

```bash
# Generate coverage report
pytest tests/ --cov=ImageComparisonSystem --cov-report=html

# View coverage in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows

# Coverage report in console
pytest tests/ --cov=ImageComparisonSystem
```

### Continuous Integration

GitHub Actions (when configured) will run:
```bash
pytest tests/ --cov=ImageComparisonSystem --cov-report=xml
```

---

## Writing New Tests

### Test Template

```python
"""
Unit tests for module_name module.
"""

import pytest
from module_name import SomeClass


@pytest.mark.unit
class TestSomeClass:
    """Test SomeClass functionality."""
    
    def test_basic_functionality(self, fixture_name):
        """Test should describe what it tests."""
        # Arrange - set up test data
        obj = SomeClass(fixture_name)
        
        # Act - perform the operation
        result = obj.do_something()
        
        # Assert - verify results
        assert result == expected_value
    
    def test_error_handling(self):
        """Test should handle error cases."""
        obj = SomeClass()
        
        with pytest.raises(ValueError):
            obj.invalid_operation()
```

### Using Fixtures

```python
def test_with_multiple_fixtures(temp_image_dir, simple_test_image, valid_config):
    """Fixtures are injected as parameters."""
    # All three fixtures are available
    assert temp_image_dir.exists()
    assert simple_test_image is not None
    assert valid_config.base_dir.exists()
```

### Creating Custom Fixtures

```python
# In conftest.py
@pytest.fixture
def my_custom_fixture():
    """Description of what this fixture provides."""
    # Setup
    setup_data = create_something()
    
    yield setup_data  # Provide to test
    
    # Teardown (optional)
    cleanup_something(setup_data)
```

---

## Best Practices

### Logging

✅ **DO:**
- Use appropriate log levels (DEBUG for details, INFO for flow, ERROR for failures)
- Include context in log messages (filenames, values, reasons)
- Use `exc_info=True` when logging exceptions
- Configure logging early in application startup

```python
logger.error(f"Failed to process {filename}: {error}", exc_info=True)
```

❌ **DON'T:**
- Use print() for application output (use logging)
- Log sensitive information (passwords, tokens)
- Use bare `except:` without logging the error
- Mix print() and logging in the same module

```python
# Bad
except Exception:
    pass

# Good
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

### Testing

✅ **DO:**
- Write isolated unit tests that don't depend on external resources
- Use fixtures for common test data
- Name tests descriptively: `test_<what>_<when>_<expected>`
- Test both happy paths and error cases
- Use markers to organize tests by type

```python
@pytest.mark.unit
def test_config_validation_fails_with_missing_directory(temp_image_dir):
    """Config validation should fail if directories don't exist."""
    config = Config(base_dir=temp_image_dir, new_dir="missing", known_good_dir="missing")
    is_valid, error_msg = config.validate()
    assert not is_valid
```

❌ **DON'T:**
- Test the test framework (test pytest itself)
- Have tests that depend on each other
- Use hard-coded paths in tests
- Skip tests without marking them explicitly
- Write tests that modify global state

```python
# Bad - test depends on file existing
def test_load_image():
    img = load_image("/absolute/path/to/image.png")

# Good - use fixture
def test_load_image(temp_image_dir, simple_test_image):
    image_path = temp_image_dir / "test.png"
    simple_test_image.save(image_path)
    img = load_image(image_path)
```

---

## Troubleshooting

### Tests Not Running

```bash
# Verify pytest can find tests
pytest --collect-only tests/

# Check pytest.ini configuration
cat pytest.ini

# Run with verbose output
pytest tests/ -vv
```

### Import Errors in Tests

```bash
# Verify PYTHONPATH includes ImageComparisonSystem
python -c "import sys; print(sys.path)"

# Run tests from repository root
cd /path/to/repo
pytest tests/
```

### Logging Not Appearing

```bash
# Verify logging is initialized in main.py
python main.py --log-level debug --base-dir /path

# Check log file permissions
ls -la app.log

# Verify log file path
python main.py --log-file /tmp/test.log
```

---

## Future Enhancements

- [ ] End-to-end integration tests
- [ ] Performance benchmarking tests
- [ ] GitHub Actions CI/CD pipeline
- [ ] HTML report generation tests
- [ ] Mock image processor for faster tests
- [ ] Test coverage threshold enforcement (>80%)
