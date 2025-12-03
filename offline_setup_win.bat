@echo off
REM Offline Setup Script for Image Comparison Tool (Windows)
REM Run this on a machine WITH internet to download all dependencies

echo ==========================================
echo Image Comparison Tool - Offline Setup
echo ==========================================
echo.

REM Create packages directory
set PACKAGE_DIR=offline_packages
if not exist "%PACKAGE_DIR%" mkdir "%PACKAGE_DIR%"

echo Creating packages directory: %PACKAGE_DIR%
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed
    echo Please install Python and pip first
    pause
    exit /b 1
)

echo Downloading dependencies...
echo ------------------------------------------

REM Download all dependencies with their dependencies
pip download ^
    "Pillow>=8.0.0,<12.0.0" ^
    "numpy>=1.19.0,<2.0.0" ^
    "opencv-python>=4.5.0" ^
    "scikit-image>=0.19.0" ^
    "matplotlib>=3.3.0" ^
    --only-binary=:all ^
    --no-deps ^
    --dest "%PACKAGE_DIR%" ^
    --python-version 3.8 ^
    --platform win_amd64

echo.
echo Download complete!
echo.

REM Create installation batch file for offline machine
(
echo @echo off
echo REM Install packages offline
echo REM Run this script on the offline machine
echo.
echo echo Installing Image Comparison Tool dependencies...
echo echo.
echo.
echo REM Install from local packages
echo pip install --no-index --find-links=. *.whl
echo.
echo echo.
echo echo Installation complete!
echo echo.
echo echo Verify installation by running:
echo echo   python ..\dependencies.py
echo pause
) > "%PACKAGE_DIR%\install_offline.bat"

REM Create README for offline installation
(
echo OFFLINE INSTALLATION INSTRUCTIONS
echo ==================================
echo.
echo This directory contains all Python packages needed to run the
echo Image Comparison Tool in an offline environment.
echo.
echo INSTALLATION STEPS:
echo -------------------
echo.
echo 1. Copy this entire 'offline_packages' directory to your offline machine
echo.
echo 2. On the offline machine, navigate to this directory
echo.
echo 3. Run: install_offline.bat
echo.
echo 4. Verify installation: python ..\dependencies.py
echo.
echo SYSTEM REQUIREMENTS:
echo --------------------
echo - Python 3.8 or higher
echo - pip package manager
echo - Windows 64-bit
echo.
echo NOTES:
echo ------
echo - tkinter is usually included with Python on Windows
echo - If you encounter issues, try updating pip first:
echo   python -m pip install --upgrade pip
echo.
echo For more help, see the main README.md
) > "%PACKAGE_DIR%\README.txt"

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Package directory created: %PACKAGE_DIR%
for /f %%i in ('dir /b "%PACKAGE_DIR%\*.whl" 2^>nul ^| find /c /v ""') do set COUNT=%%i
echo Total packages downloaded: %COUNT%
echo.
echo NEXT STEPS:
echo 1. Copy the '%PACKAGE_DIR%' directory to your offline machine
echo 2. On the offline machine, run:
echo    cd %PACKAGE_DIR%
echo    install_offline.bat
echo.
echo See %PACKAGE_DIR%\README.txt for detailed instructions
echo.
pause
