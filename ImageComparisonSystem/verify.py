#!/usr/bin/env python3
"""
Installation verification script.
Tests all dependencies and core functionality.
"""

import sys
import os
import logging

# Setup logging - verify.py is user-facing so we use print for output
logger = logging.getLogger("ImageComparison")

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def print_section(text):
    """Print a section header."""
    print("\n" + text)
    print("-" * 70)

def test_imports():
    """Test that all required modules can be imported."""
    print_section("Testing Module Imports")
    logger.debug("Starting module import tests")
    
    modules = {
        'PIL': 'Pillow (image processing)',
        'numpy': 'NumPy (array operations)',
        'cv2': 'OpenCV (computer vision)',
        'skimage': 'scikit-image (SSIM calculation)',
        'matplotlib': 'Matplotlib (histogram visualization)',
        'tkinter': 'tkinter (GUI - optional for CLI usage)'
    }
    
    all_success = True
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✓ {module:15s} - {description}")
            logger.debug(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module:15s} - FAILED: {e}")
            logger.warning(f"Failed to import {module}: {e}")
            all_success = False
    
    logger.info(f"Module import tests {'passed' if all_success else 'failed'}")
    return all_success

def test_core_modules():
    """Test that project modules can be imported."""
    print_section("Testing Project Modules")
    logger.debug("Starting project module import tests")
    
    modules = [
        'dependencies',
        'config',
        'ui',
        'analyzers',
        'processor',
        'comparator',
        'report_generator'
    ]
    
    all_success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py")
            logger.debug(f"✓ {module} module imported successfully")
        except ImportError as e:
            print(f"✗ {module}.py - FAILED: {e}")
            logger.error(f"Failed to import {module}: {e}")
            all_success = False
        except Exception as e:
            print(f"✗ {module}.py - ERROR: {e}")
            logger.error(f"Error importing {module}: {e}", exc_info=True)
            all_success = False
    
    logger.info(f"Project module tests {'passed' if all_success else 'failed'}")
    return all_success

def test_basic_functionality():
    """Test basic image processing functionality."""
    print_section("Testing Basic Functionality")
    logger.debug("Starting basic functionality tests")
    
    try:
        import numpy as np
        from PIL import Image
        import cv2
        
        # Test 1: Create test image
        print("Creating test image...", end=" ")
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(test_img)
        print("✓")
        logger.debug("Test image created successfully")
        
        # Test 2: Image operations
        print("Testing image operations...", end=" ")
        gray = cv2.cvtColor(test_img, cv2.COLOR_RGB2GRAY)
        assert gray.shape == (100, 100)
        print("✓")
        logger.debug("Image operations test passed")
        
        # Test 3: Histogram calculation
        print("Testing histogram calculation...", end=" ")
        hist, _ = np.histogram(test_img[:,:,0], bins=256, range=(0, 256))
        assert len(hist) == 256
        print("✓")
        logger.debug("Histogram calculation test passed")
        
        # Test 4: SSIM
        print("Testing SSIM calculation...", end=" ")
        from skimage.metrics import structural_similarity as ssim
        test_img2 = test_img.copy()
        ssim_val = ssim(gray, cv2.cvtColor(test_img2, cv2.COLOR_RGB2GRAY))
        assert 0 <= ssim_val <= 1
        print("✓")
        logger.debug("SSIM calculation test passed")
        
        # Test 5: Matplotlib
        print("Testing matplotlib (non-interactive)...", end=" ")
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        plt.close(fig)
        print("✓")
        logger.debug("Matplotlib test passed")
        
        logger.info("All basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"\n✗ Functionality test failed: {e}")
        logger.error(f"Functionality test failed: {e}", exc_info=True)
        return False

def test_config_creation():
    """Test configuration object creation."""
    print_section("Testing Configuration")
    logger.debug("Starting config creation tests")
    
    try:
        from config import Config
        from pathlib import Path
        
        print("Creating Config object...", end=" ")
        config = Config(
            base_dir=Path("."),
            new_dir="test_new",
            known_good_dir="test_good"
        )
        print("✓")
        logger.debug("Config object created successfully")
        
        print("Testing config properties...", end=" ")
        assert hasattr(config, 'use_histogram_equalization')
        assert hasattr(config, 'highlight_color')
        assert hasattr(config, 'pixel_diff_threshold')
        print("✓")
        logger.debug("Config properties verified")
        
        logger.info("Config creation tests passed")
        return True
        
    except Exception as e:
        print(f"\n✗ Config test failed: {e}")
        logger.error(f"Config test failed: {e}", exc_info=True)
        return False

def test_analyzers():
    """Test analyzer registry."""
    print_section("Testing Analyzers")
    logger.debug("Starting analyzer registry tests")
    
    try:
        import numpy as np
        from analyzers import AnalyzerRegistry
        
        print("Creating AnalyzerRegistry...", end=" ")
        registry = AnalyzerRegistry()
        print("✓")
        logger.debug(f"AnalyzerRegistry created with {len(registry.analyzers)} analyzers")
        
        print("Testing analyzers on sample images...", end=" ")
        img1 = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        img2 = img1.copy()
        results = registry.analyze_all(img1, img2)
        
        assert 'Pixel Difference' in results
        assert 'Structural Similarity' in results
        assert 'Histogram Analysis' in results
        print("✓")
        logger.debug("All analyzer tests passed")
        
        print(f"Registered analyzers: {len(registry.analyzers)}")
        for analyzer in registry.analyzers:
            print(f"  - {analyzer.name}")
            logger.debug(f"Analyzer registered: {analyzer.name}")
        
        logger.info("Analyzer tests passed")
        return True
        
    except Exception as e:
        print(f"\n✗ Analyzer test failed: {e}")
        logger.error(f"Analyzer test failed: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests."""
    print_header("Image Comparison Tool - INSTALLATION VERIFICATION")
    logger.info("Starting installation verification")
    
    print("\nPython version:", sys.version)
    print("Platform:", sys.platform)
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {sys.platform}")
    
    # Run all tests
    tests = [
        ("Dependencies", test_imports),
        ("Project Modules", test_core_modules),
        ("Basic Functionality", test_basic_functionality),
        ("Configuration", test_config_creation),
        ("Analyzers", test_analyzers)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            logger.error(f"{test_name} test crashed: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status:10s} - {test_name}")
        logger.info(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe Image Comparison Tool is ready to use.")
        print("Run 'python main.py --help' to get started.")
        logger.info("✓ ALL VERIFICATION TESTS PASSED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease check the errors above and ensure all dependencies")
        print("are properly installed. Run 'python dependencies.py' for")
        print("detailed dependency information.")
        logger.warning("✗ Some verification tests failed")
        return 1

if __name__ == '__main__':
    exit_code = main()
    
    # Keep console window open on Windows
    if sys.platform == 'win32':
        input("\nPress Enter to close this window...")
    
    sys.exit(exit_code)
