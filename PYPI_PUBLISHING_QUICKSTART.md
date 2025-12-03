# Quick Start: Building and Publishing to PyPI

## 1-Minute Setup

### Install Build Tools

```bash
pip install build twine
```

### Build the Package

```bash
python -m build
```

This creates two files in `dist/`:
- `image-comparison-system-1.0.0.tar.gz` (source distribution)
- `image-comparison-system-1.0.0-py3-none-any.whl` (wheel distribution)

### Verify Build

```bash
python -m twine check dist/*
```

Expected output:
```
Checking dist/image_comparison_system-1.0.0-py3-none-any.whl: PASSED
Checking dist/image_comparison_system-1.0.0.tar.gz: PASSED
```

## Publishing Options

### Option 1: Automated (GitHub Actions) - Recommended

```bash
# Create and push a release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions automatically:
# 1. Runs all tests
# 2. Builds the package
# 3. Publishes to PyPI
```

**Setup required:**
- Configure Trusted Publishers in PyPI settings
- Add GitHub repository details to PyPI account

### Option 2: Manual Upload

#### Test First (TestPyPI)

```bash
# Set up PyPI token from https://test.pypi.org/
python -m twine upload -r testpypi dist/*

# Install to verify
pip install -i https://test.pypi.org/simple/ image-comparison-system==1.0.0
```

#### Publish to PyPI

```bash
# Set up PyPI token from https://pypi.org/
python -m twine upload dist/*

# Verify on PyPI
pip install image-comparison-system
```

## Pre-Publication Checklist

```bash
# 1. Update version
# Edit: setup.py and pyproject.toml
# Change version = "1.0.0" to version = "1.0.1"

# 2. Run tests
pytest tests/ -v

# 3. Format code
black ImageComparisonSystem tests

# 4. Clean old builds
rm -rf build/ dist/ *.egg-info

# 5. Build new package
python -m build

# 6. Verify
python -m twine check dist/*

# 7. Update CHANGELOG.md
# Add entry for new version

# 8. Commit and tag
git add .
git commit -m "Release v1.0.1"
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin main
git push origin v1.0.1
```

## After Publishing

### Verify Installation Works

```bash
# Install from PyPI (global)
pip install image-comparison-system

# Or upgrade
pip install --upgrade image-comparison-system

# Test import
python -c "from ImageComparisonSystem import ImageComparator; print('✓ Success')"

# Test CLI tools
imgcompare --help
imgcompare-check
```

### Check Package on PyPI

Visit: https://pypi.org/project/image-comparison-system/

## Files Created for Publishing

### Core Configuration
- `pyproject.toml` - Modern Python package configuration (PEP 518)
- `setup.py` - Traditional setup script
- `setup.cfg` - Setup configuration
- `MANIFEST.in` - Specifies which files to include in distribution

### GitHub Actions Workflows
- `.github/workflows/tests.yml` - Runs tests on every push/PR
- `.github/workflows/publish-to-pypi.yml` - Publishes on release

### Documentation
- `PYPI_PUBLISHING.md` - Complete publishing guide
- This file - Quick reference

## Troubleshooting

### "Distribution already exists"
- Version already published to PyPI
- Solution: Increment version number (1.0.0 → 1.0.1)

### "Tests failing"
- Fix failing tests before publishing
- Run: `pytest tests/ -v`

### "Build has errors"
- Check setup.py/pyproject.toml for typos
- Verify all dependencies are listed
- Run: `python -m build`

### "Import errors after install"
- Check Python version (needs 3.8+)
- Verify dependencies installed: `pip install -e ".[dev]"`

## Versioning

This project uses [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

1.0.0  → Initial release
1.0.1  → Bug fix
1.1.0  → New feature
2.0.0  → Breaking change
```

## Command Reference

```bash
# Build locally
python -m build

# Verify build
python -m twine check dist/*

# Upload to TestPyPI
python -m twine upload -r testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install image-comparison-system

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ image-comparison-system

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
black --check ImageComparisonSystem
flake8 ImageComparisonSystem
mypy ImageComparisonSystem
```

## Next Steps

1. **First Time Publishing?**
   - Read: `PYPI_PUBLISHING.md` (complete guide)
   - Account setup: https://pypi.org/
   - Trusted Publishers: https://docs.pypi.org/trusted-publishers/

2. **Ready to Publish?**
   - Follow pre-publication checklist above
   - Push release tag: `git push origin v1.0.0`
   - Watch GitHub Actions: Actions tab in repository

3. **Need Help?**
   - Check: `PYPI_PUBLISHING.md` troubleshooting section
   - PyPI Help: https://pypi.org/help/
   - Open issue: https://github.com/sjbudlong/ImageComparisonTool/issues

---

**Current Package Status**: ✅ Ready for Publishing
- Version: 1.0.0
- Python: 3.8+
- License: MIT
- Tests: 127/127 passing
