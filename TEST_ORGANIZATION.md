# Test File Organization Guide

## Quick Reference

### Automated Unit Tests (pytest)
**Location:** `tests/` directory  
**Run:** `pytest tests/`  
**Type:** Automated, isolated, reproducible  
**Purpose:** CI/CD, regression testing, code validation  

```
tests/
├── test_config.py           ← Config validation
├── test_models.py           ← Data serialization
├── test_processor.py        ← Image processing
└── test_dependencies.py     ← Dependency checking
```

### Manual Test Scripts
**Location:** Repository root  
**Run:** `./test_*.bat` or `./test_*.sh`  
**Type:** Manual demonstration, integration  
**Purpose:** Quick validation, CLI examples  

```
./test_basic_cli.bat        ← Basic CLI usage
./test_3d_rendering.bat     ← 3D render comparison
./test_full_options.bat     ← All CLI flags
./test_strict_comparison.bat ← Strict thresholds
./test_lenient_comparison.bat ← Lenient thresholds
./test_with_report.bat      ← Auto-open report
```

---

## Comparison Table

| Aspect | Automated Tests | Manual Test Scripts |
|--------|-----------------|-------------------|
| **Location** | `tests/` | Root directory |
| **Command** | `pytest tests/` | `./test_*.bat` or `./*.sh` |
| **Scope** | Individual functions | Full workflows |
| **Speed** | Fast (<5s) | Slower (creates output) |
| **Output** | Test pass/fail | HTML reports, JSON |
| **CI/CD** | ✅ Integrated | ⚠️ Manual only |
| **Dependencies** | pytest only | All project deps |
| **Data** | Temp/fixtures | Real image dirs |
| **Maintenance** | Easy to extend | Manual updates |

---

## When to Use Which

### Use Automated Tests (`pytest`)
- ✅ Adding new features → write test first
- ✅ Fixing bugs → add regression test
- ✅ Refactoring code → verify tests still pass
- ✅ CI/CD pipeline → run before merging
- ✅ Quick validation → fast feedback
- ✅ Coverage reports → measure code coverage

### Use Manual Test Scripts
- ✅ Demonstrating CLI capabilities
- ✅ Testing with real images
- ✅ Validating HTML report generation
- ✅ Checking command-line argument combinations
- ✅ Manual QA verification
- ✅ Showcasing features to users

---

## Example Workflow

### Development Cycle
```
1. Write unit test          → pytest tests/test_new_feature.py
2. Implement feature       → edit ImageComparisonSystem/module.py
3. Run all tests           → pytest tests/
4. Test CLI integration    → ./test_full_options.bat
5. Check coverage          → pytest --cov=ImageComparisonSystem
6. Commit                  → git commit
7. CI/CD runs all tests    → GitHub Actions
```

### Feature Development
```python
# tests/test_feature.py
@pytest.mark.unit
def test_new_feature(valid_config):
    """Test new feature with fixtures."""
    result = my_new_feature(valid_config)
    assert result.success

# Then implement:
# ImageComparisonSystem/module.py
def my_new_feature(config):
    # Implementation
    return result

# Verify:
pytest tests/test_feature.py -v
```

### User Demonstration
```bash
# Show basic usage
./test_basic_cli.bat

# Show advanced features
./test_full_options.bat

# Generate actual reports
./test_with_report.bat
```

---

## File Locations on Disk

```
ImageComparisonTool/
│
├── tests/                          ← AUTOMATED TESTS
│   ├── __init__.py
│   ├── conftest.py                 (fixtures, configuration)
│   ├── test_config.py              (10 tests)
│   ├── test_models.py              (4 tests)
│   ├── test_processor.py           (7 tests)
│   ├── test_dependencies.py        (7 tests)
│   ├── fixtures/                   (test images - future)
│   └── integration/                (e2e tests - future)
│
├── test_basic_cli.bat              ← MANUAL TEST SCRIPTS
├── test_basic_cli.sh
├── test_3d_rendering.bat
├── test_3d_rendering.sh
├── test_full_options.bat
├── test_full_options.sh
├── test_strict_comparison.bat
├── test_strict_comparison.sh
├── test_lenient_comparison.bat
├── test_lenient_comparison.sh
├── test_with_report.bat
├── test_with_report.sh
├── TEST_FILES_README.md             (Manual test documentation)
│
├── ImageComparisonSystem/           ← MAIN CODE
│   ├── main.py
│   ├── config.py
│   ├── comparator.py
│   ├── logging_config.py
│   └── ...
│
├── TESTING.md                       ← TEST DOCUMENTATION
├── IMPLEMENTATION_SUMMARY.md        ← THIS SUMMARY
└── pytest.ini                       ← PYTEST CONFIGURATION
```

---

## Running Tests: Command Reference

### Automated Tests
```bash
# Run all automated tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfig::test_config_validation

# Run only unit tests
pytest tests/ -m unit

# Run with coverage
pytest tests/ --cov=ImageComparisonSystem

# Run and exit on first failure
pytest tests/ -x

# Run tests in parallel
pytest tests/ -n 4  # requires pytest-xdist
```

### Manual Test Scripts
```bash
# Windows
test_basic_cli.bat
test_full_options.bat
test_with_report.bat

# Linux/Mac
./test_basic_cli.sh
./test_full_options.sh
./test_with_report.sh
```

---

## Integration

### GitHub Actions (Recommended)
```yaml
# .github/workflows/tests.yml
- name: Run unit tests
  run: pytest tests/ --cov=ImageComparisonSystem
```

### Local Development
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests before committing
pytest tests/

# Check coverage
pytest tests/ --cov
```

---

## Summary

**Separation keeps things clean:**
- 🧪 Automated unit tests in `tests/` for CI/CD
- 📝 Manual test scripts in root for demonstrations
- ✅ Both can coexist without interference
- 📊 Easy to measure code quality with pytest
- 🎯 Easy to validate features with manual tests
