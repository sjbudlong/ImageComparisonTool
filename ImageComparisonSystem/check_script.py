#!/usr/bin/env python3
"""
Quick system check script.
Verifies Python version and critical dependencies.
"""

import sys


def check_python_version():
    """Check if Python version meets requirements."""
    required = (3, 8)
    current = sys.version_info[:2]

    print(f"Python version: {sys.version}")

    if current >= required:
        print(
            f"✓ Python {current[0]}.{current[1]} meets requirement (>= {required[0]}.{required[1]})"
        )
        return True
    else:
        print(
            f"✗ Python {current[0]}.{current[1]} does not meet requirement (>= {required[0]}.{required[1]})"
        )
        print(f"  Please upgrade Python")
        return False


def check_critical_dependencies():
    """Check critical dependencies only."""
    critical = {"numpy": "NumPy", "PIL": "Pillow", "cv2": "OpenCV"}

    print("\nChecking critical dependencies:")
    all_ok = True

    for module, name in critical.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT INSTALLED")
            all_ok = False

    return all_ok


def main():
    """Run quick system check."""
    print("=" * 60)
    print("Image Comparison Tool - QUICK SYSTEM CHECK")
    print("=" * 60)
    print()

    python_ok = check_python_version()
    deps_ok = check_critical_dependencies()

    print()
    print("=" * 60)

    if python_ok and deps_ok:
        print("✓ System ready!")
        print("\nFor detailed check, run:")
        print("  python dependencies.py")
        print("  python verify_installation.py")
        return 0
    else:
        print("✗ System not ready")
        print("\nIssues found:")
        if not python_ok:
            print("  - Python version too old")
        if not deps_ok:
            print("  - Missing critical dependencies")
        print("\nRun for detailed information:")
        print("  python dependencies.py")
        return 1


if __name__ == "__main__":
    exit_code = main()

    # Keep console window open on Windows
    if sys.platform == "win32":
        input("\nPress Enter to close this window...")

    sys.exit(exit_code)
