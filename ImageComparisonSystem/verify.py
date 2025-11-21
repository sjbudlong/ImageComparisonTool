#!/usr/bin/env python3
"""
Installation verification script.
Tests all dependencies and core functionality.
"""

import sys
import os

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
        except ImportError as e:
            print(f"✗ {module:15s} - FAILED: {e}")
            all_success = False
    
    return all_success

def test_core_modules():
    """Test that project modules can be imported."""
    print_section("Testing Project Modules")
    
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
        except ImportError as e:
            print(f"✗ {module}.py - FAILED: {e}")
            all_success = False
        except Exception as e:
            print(f"✗ {module}.py - ERROR: {e}")
            all_success = False
    
    return all_success

def test_basic_functionality():
    """Test basic image processing functionality."""
    print_section("Testing Basic Functionality")
    
    try:
        import numpy as np
        from PIL import Image
        import cv2
        
        # Test 1: Create test image
        print("Creating test image...", end=" ")
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(test_img)
        print("✓")
        
        # Test 2: Image operations
        print("Testing image operations...", end=" ")
        gray = cv2.cvtColor(test_img, cv2.COLOR_RGB2GRAY)
        assert gray.shape == (100, 100)
        print("✓")
        
        # Test 3: Histogram calculation
        print("Testing histogram calculation...", end=" ")
        hist, _ = np.histogram(test_img[:,:,0], bins=256, range=(0, 256))
        assert len(hist) == 256
        print("✓")
        
        # Test 4: SSIM
        print("Testing SSIM calculation...", end=" ")
        from skimage.metrics import structural_similarity as ssim
        test_img2 = test_img.copy()
        ssim_val = ssim(gray, cv2.cvtColor(test_img2, cv2.COLOR_RGB2GRAY))
        assert 0 <= ssim_val <= 1
        print("✓")
        
        # Test 5: Matplotlib
        print("Testing matplotlib (non-interactive)...", end=" ")
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        plt.close(fig)
        print("✓")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Functionality test failed: {e}")
        return False

def test_config_creation():
    """Test configuration object creation."""
    print_section("Testing Configuration")
    
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
        
        print("Testing config properties...", end=" ")
        assert hasattr(config, 'use_histogram_equalization')
        assert hasattr(config, 'highlight_color')
        assert hasattr(config, 'pixel_diff_threshold')
        print("✓")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Config test failed: {e}")
        return False

def test_analyzers():
    """Test analyzer registry."""
    print_section("Testing Analyzers")
    
    try:
        import numpy as np
        from analyzers import AnalyzerRegistry
        
        print("Creating AnalyzerRegistry...", end=" ")
        registry = AnalyzerRegistry()
        print("✓")
        
        print("Testing analyzers on sample images...", end=" ")
        img1 = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        img2 = img1.copy()
        results = registry.analyze_all(img1, img2)
        
        assert 'Pixel Difference' in results
        assert 'Structural Similarity' in results
        assert 'Histogram Analysis' in results
        print("✓")
        
        print(f"Registered analyzers: {len(registry.analyzers)}")
        for analyzer in registry.analyzers:
            print(f"  - {analyzer.name}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests."""
    print_header("Image Comparison Tool - INSTALLATION VERIFICATION")
    
    print("\nPython version:", sys.version)
    print("Platform:", sys.platform)
    
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
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status:10s} - {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe Image Comparison Tool is ready to use.")
        print("Run 'python main.py --help' to get started.")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease check the errors above and ensure all dependencies")
        print("are properly installed. Run 'python dependencies.py' for")
        print("detailed dependency information.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    
    # Keep console window open on Windows
    if sys.platform == 'win32':
        input("\nPress Enter to close this window...")
    
    sys.exit(exit_code)
