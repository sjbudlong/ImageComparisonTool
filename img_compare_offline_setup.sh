#!/bin/bash
# Offline Setup Script for Image Comparison Tool
# Run this on a machine WITH internet to download all dependencies

set -e

echo "=========================================="
echo "Image Comparison Tool - Offline Setup"
echo "=========================================="
echo ""

# Create packages directory
PACKAGE_DIR="offline_packages"
mkdir -p "$PACKAGE_DIR"

echo "Creating packages directory: $PACKAGE_DIR"
echo ""

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed"
    echo "Please install Python and pip first"
    exit 1
fi

echo "Downloading dependencies..."
echo "------------------------------------------"

# Download all dependencies with their dependencies
pip download \
    "Pillow>=8.0.0,<12.0.0" \
    "numpy>=1.19.0,<2.0.0" \
    "opencv-python>=4.5.0" \
    "scikit-image>=0.19.0" \
    "matplotlib>=3.3.0" \
    --dest "$PACKAGE_DIR" \
    --python-version 3.8 \
    --platform manylinux2014_x86_64 \
    --platform win_amd64 \
    --platform macosx_10_9_x86_64

echo ""
echo "✓ Download complete!"
echo ""

# Create installation script for offline machine
cat > "$PACKAGE_DIR/install_offline.sh" << 'EOF'
#!/bin/bash
# Install packages offline
# Run this script on the offline machine

echo "Installing Image Comparison Tool dependencies..."
echo ""

# Install from local packages
pip install --no-index --find-links=. *.whl

echo ""
echo "✓ Installation complete!"
echo ""
echo "Verify installation by running:"
echo "  python ../dependencies.py"
EOF

chmod +x "$PACKAGE_DIR/install_offline.sh"

# Create Windows installation script
cat > "$PACKAGE_DIR/install_offline.bat" << 'EOF'
@echo off
REM Install packages offline on Windows
REM Run this script on the offline machine

echo Installing Image Comparison Tool dependencies...
echo.

REM Install from local packages
pip install --no-index --find-links=. *.whl

echo.
echo Installation complete!
echo.
echo Verify installation by running:
echo   python ..\dependencies.py
pause
EOF

# Create README for offline installation
cat > "$PACKAGE_DIR/README.txt" << 'EOF'
OFFLINE INSTALLATION INSTRUCTIONS
==================================

This directory contains all Python packages needed to run the
Image Comparison Tool in an offline environment.

INSTALLATION STEPS:
-------------------

1. Copy this entire 'offline_packages' directory to your offline machine

2. On the offline machine, navigate to this directory

3. Run the installation script:

   Linux/Mac:
   ----------
   chmod +x install_offline.sh
   ./install_offline.sh

   Windows:
   --------
   install_offline.bat

4. Verify installation:
   python ../dependencies.py

SYSTEM REQUIREMENTS:
--------------------
- Python 3.8 or higher
- pip package manager

NOTES:
------
- tkinter requires system-level installation:
  Ubuntu/Debian: sudo apt-get install python3-tk
  Fedora/RHEL:   sudo dnf install python3-tkinter
  macOS:         Usually included with Python
  Windows:       Usually included with Python

- If you encounter architecture mismatches, re-download packages
  on the online machine using the correct platform:
  pip download <package> --platform <your_platform>

TROUBLESHOOTING:
----------------
If installation fails, try:
1. Update pip: pip install --upgrade pip
2. Install packages one at a time to identify problematic packages
3. Check Python version compatibility

For more help, see the main README.md
EOF

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Package directory created: $PACKAGE_DIR"
echo "Total packages downloaded: $(ls -1 $PACKAGE_DIR/*.whl 2>/dev/null | wc -l)"
echo ""
echo "NEXT STEPS:"
echo "1. Copy the '$PACKAGE_DIR' directory to your offline machine"
echo "2. On the offline machine, run:"
echo "   cd $PACKAGE_DIR"
echo "   ./install_offline.sh    (Linux/Mac)"
echo "   or"
echo "   install_offline.bat     (Windows)"
echo ""
echo "See $PACKAGE_DIR/README.txt for detailed instructions"
echo ""
