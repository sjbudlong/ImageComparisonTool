# Contributing to Image Comparison Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Output of `python dependencies.py`

### Suggesting Features

Feature requests are welcome! Please:
- Check existing issues first
- Describe the use case
- Explain why this would be useful
- Provide examples if possible

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/sjbudlong/ImageComparisonTool.git
   cd image-comparison-system
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation
   - Run verification: `python verify_installation.py`

4. **Test your changes**
   ```bash
   # Run dependency check
   python dependencies.py
   
   # Run verification tests
   python verify_installation.py
   
   # Test with sample data
   python main.py --base-dir ./test --new-dir new --known-good-dir baseline
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Use clear commit messages:
   - `feat: Add new analyzer for edge detection`
   - `fix: Correct histogram equalization for grayscale images`
   - `docs: Update installation instructions`
   - `refactor: Simplify config validation`

6. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a PR on GitHub with:
   - Description of changes
   - Related issue numbers
   - Screenshots if UI changes

## Adding New Analyzers

The system is designed to be modular. To add a new analyzer:

```python
from analyzers import ImageAnalyzer

class MyCustomAnalyzer(ImageAnalyzer):
    @property
    def name(self) -> str:
        return "My Custom Metric"
    
    def analyze(self, img1: np.ndarray, img2: np.ndarray) -> dict:
        # Your analysis logic
        result = calculate_something(img1, img2)
        
        return {
            'metric_name': result,
            'another_metric': other_value
        }
```

Then register in `AnalyzerRegistry._register_default_analyzers()`:
```python
self.register(MyCustomAnalyzer())
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document classes and functions with docstrings
- Keep functions focused and modular
- Add comments for complex logic

## Testing

Before submitting:
- Ensure all existing tests pass
- Add tests for new features
- Test on multiple platforms if possible
- Verify offline installation works

## Documentation

Update documentation for:
- New features or options
- Changed behavior
- New dependencies
- Configuration options

## Questions?

Feel free to open an issue for questions or discussion!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
