# PyPI Publishing Guide

This document describes how to build and publish the Image Comparison System to PyPI (Python Package Index).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Building the Package](#building-the-package)
- [Publishing to TestPyPI](#publishing-to-testpypi)
- [Publishing to PyPI](#publishing-to-pypi)
- [Automated Publishing (GitHub Actions)](#automated-publishing-github-actions)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

1. **Python 3.8+** - The package supports Python 3.8 through 3.13
2. **pip** - Python package installer
3. **build** - PEP 517 compliant build tool
4. **twine** - Utility for publishing packages to PyPI
5. **Git** - For version control

### PyPI Account Setup

1. Create a free account at https://pypi.org/
2. Create a separate test account at https://test.pypi.org/
3. Generate API tokens for both accounts:
   - Go to Account Settings → API tokens
   - Create token with "Entire repository" scope

## Local Development Setup

### 1. Install Development Dependencies

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install individual tools
pip install build twine pytest pytest-cov black flake8 mypy
```

### 2. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ImageComparisonSystem --cov-report=html

# Run specific test module
pytest tests/test_comparator.py -v
```

### 3. Format Code

```bash
# Check formatting
black --check ImageComparisonSystem tests

# Auto-format code
black ImageComparisonSystem tests
```

### 4. Run Linting

```bash
# Run flake8
flake8 ImageComparisonSystem tests

# Run mypy
mypy ImageComparisonSystem --ignore-missing-imports
```

## Building the Package

### Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info
# On Windows
rmdir /s build dist *.egg-info
```

### Create Distributions

```bash
# Build source distribution (.tar.gz) and wheel (.whl)
python -m build

# The build/ directory now contains:
# - dist/image-comparison-system-1.0.0.tar.gz (source)
# - dist/image-comparison-system-1.0.0-py3-none-any.whl (wheel)
```

### Verify Build

```bash
# Check distribution validity
twine check dist/*

# View package contents (optional)
tar -tzf dist/image-comparison-system-1.0.0.tar.gz | head -20
```

## Publishing to TestPyPI

### Step 1: Upload to TestPyPI

```bash
# Using Trusted Publisher (GitHub Actions recommended):
twine upload -r testpypi dist/*

# Or with username/password (less secure):
twine upload -r testpypi -u __token__ -p your_test_api_token dist/*
```

### Step 2: Verify on TestPyPI

```bash
# Visit: https://test.pypi.org/project/image-comparison-system/

# Install from TestPyPI to verify
pip install -i https://test.pypi.org/simple/ image-comparison-system==1.0.0
```

### Step 3: Test Installation

```bash
# Test command-line tools
imgcompare --help
imgcompare-check --help

# Test Python import
python -c "from ImageComparisonSystem import ImageComparator; print('✓ Import successful')"
```

## Publishing to PyPI

### Step 1: Tag Release in Git

```bash
# Create and push a git tag (triggers automated publishing)
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Or manually upload to PyPI:
twine upload dist/*
```

### Step 2: Verify on PyPI

```bash
# Visit: https://pypi.org/project/image-comparison-system/

# Install from PyPI
pip install image-comparison-system

# Test installation
imgcompare --help
```

### Step 3: Create GitHub Release

1. Go to https://github.com/sjbudlong/ImageComparisonTool/releases
2. Create new release for tag
3. Add release notes
4. Attach distribution files from `dist/` directory

## Automated Publishing (GitHub Actions)

### Prerequisites

1. **Set Up GitHub Secrets**

   For TestPyPI:
   - Go to repository Settings → Secrets and Variables → Actions
   - Add `PYPI_TEST_TOKEN` with your TestPyPI API token

   For PyPI:
   - Add `PYPI_TOKEN` with your PyPI API token

   **Alternative: Use Trusted Publishers** (Recommended)
   - No secrets needed
   - Add trusted publisher in PyPI account settings
   - Configure with GitHub repo details

2. **Configure Trusted Publishers** (Recommended)

   ```
   PyPI Settings → Trusted Publishers → Add New Publisher
   - GitHub Repository: sjbudlong/ImageComparisonTool
   - Workflow: publish-to-pypi.yml
   - Environment: pypi
   ```

### Publishing Workflows

#### Automatic (on Release)

```bash
# Create and push a release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create GitHub release
# → Automatically triggers publish-to-pypi.yml
# → Builds and publishes to PyPI
```

#### Manual (via Workflow Dispatch)

```bash
# Go to GitHub Actions → Publish to PyPI
# Select "Run workflow"
# Choose environment: testpypi or pypi
```

#### Tests Run First

Every push to main/develop and PR triggers:
- Unit tests across Python 3.8-3.13
- Tests on Ubuntu, Windows, macOS
- Linting checks (black, flake8, mypy)
- Package build verification

## Verification

### Post-Publication Checklist

```bash
# 1. Check PyPI page
# https://pypi.org/project/image-comparison-system/

# 2. Install from PyPI
pip install image-comparison-system

# 3. Verify version
python -c "import ImageComparisonSystem; print(ImageComparisonSystem.__version__)"

# 4. Test command-line
imgcompare --help
imgcompare-deps

# 5. Run quick comparison
# (with sample images)
imgcompare --base-dir /path/to/images --new-dir new --known-good-dir known_good

# 6. Check documentation
# https://github.com/sjbudlong/ImageComparisonTool#readme
```

### Documentation Updates

After publishing, update:

1. **GitHub Release Notes** - Describe changes and new features
2. **CHANGELOG.md** - Add entry for new version
3. **README.md** - Update installation instructions if needed
4. **Project Wiki** - Add deployment notes
5. **GitHub Project** - Mark version milestone as complete

## Troubleshooting

### Common Issues

#### 1. "Invalid distribution" error

```bash
# Solution: Verify distribution with twine
twine check dist/*

# Common causes:
# - Missing required metadata in setup.py
# - Invalid README format
# - Non-ASCII characters in metadata
```

#### 2. "You are not allowed to upload" error

```bash
# Solution: Check API token
# - Token may be expired (regenerate if > 30 days old)
# - Token may have wrong permissions
# - Using wrong repository URL

# Re-authenticate
twine upload -r pypi --verbose dist/*
```

#### 3. "File already exists" error

```bash
# Solution: Cannot overwrite versions on PyPI
# Must use new version number

# Options:
# 1. Publish as new version: v1.0.1, v1.1.0, etc.
# 2. Delete previous version (if <24h old)
# 3. Use TestPyPI for testing
```

#### 4. Build fails during GitHub Actions

```bash
# Check workflow logs: https://github.com/.../actions/runs/...

# Common causes:
# - Tests failing
# - Missing dependencies
# - Syntax errors

# Fix and push new code to retrigger
git push origin main
```

#### 5. ImportError after installation

```bash
# Solution: Check environment
# - Correct Python version? (3.8+)
# - All dependencies installed?
pip install -e ".[dev]"

# Verify installation
pip show image-comparison-system
python -c "from ImageComparisonSystem import ImageComparator; print('OK')"
```

### Getting Help

- **PyPI Help**: https://pypi.org/help/
- **Twine Documentation**: https://twine.readthedocs.io/
- **setuptools Guide**: https://setuptools.pypa.io/
- **GitHub Actions**: https://docs.github.com/en/actions/

## Version Management

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

Examples:
- **1.0.0** - Initial release
- **1.1.0** - New features (backward compatible)
- **1.0.1** - Bug fixes
- **2.0.0** - Breaking changes

### Release Checklist

Before publishing a new version:

- [ ] Update version in `setup.py` and `pyproject.toml`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Check code formatting: `black --check ImageComparisonSystem`
- [ ] Run linting: `flake8 ImageComparisonSystem`
- [ ] Build locally: `python -m build`
- [ ] Verify build: `twine check dist/*`
- [ ] Create git tag: `git tag -a v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Create GitHub release with notes

## Resources

- **PyPI Official**: https://pypi.org/
- **Setuptools Docs**: https://setuptools.pypa.io/
- **Python Packaging Guide**: https://packaging.python.org/
- **PEP 517** (Build system interface): https://peps.python.org/pep-0517/
- **PEP 518** (Build requires): https://peps.python.org/pep-0518/
- **PEP 625** (Wheel binary format): https://peps.python.org/pep-0625/

---

**Questions?** Open an issue on GitHub: https://github.com/sjbudlong/ImageComparisonTool/issues
