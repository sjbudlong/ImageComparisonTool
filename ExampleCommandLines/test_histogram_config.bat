@echo off
REM Test: Histogram Visualization Configuration
REM This demonstrates various histogram configuration options

cd /d "%~dp0"
cd ImageComparisonSystem

REM Example 1: Smooth histogram with fewer bins (overview)
echo ============================================================
echo Test 1: Smooth Histogram (64 bins) for Overview
echo ============================================================

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --histogram-bins 64 ^
  --histogram-width 14 ^
  --histogram-height 5 ^
  --histogram-gray-alpha 0.8 ^
  --histogram-rgb-alpha 0.8 ^
  --skip-dependency-check

echo.
echo Press any key to continue to next test...
pause

REM Example 2: Detailed histogram with more bins (high detail)
echo ============================================================
echo Test 2: Detailed Histogram (512 bins) for High Detail
echo ============================================================

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --histogram-bins 512 ^
  --histogram-width 18 ^
  --histogram-height 7 ^
  --histogram-gray-alpha 0.9 ^
  --histogram-rgb-alpha 0.85 ^
  --skip-dependency-check

echo.
echo Press any key to continue to next test...
pause

REM Example 3: Large figure for presentations
echo ============================================================
echo Test 3: Large Histogram for Presentations
echo ============================================================

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --histogram-bins 256 ^
  --histogram-width 20 ^
  --histogram-height 8 ^
  --histogram-gray-linewidth 2.5 ^
  --histogram-rgb-linewidth 2.0 ^
  --skip-dependency-check

echo.
echo Press any key to continue to next test...
pause

REM Example 4: Minimal histogram (only grayscale)
echo ============================================================
echo Test 4: Grayscale Only Histogram
echo ============================================================

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --histogram-bins 256 ^
  --histogram-width 12 ^
  --histogram-height 4 ^
  --show-grayscale ^
  --skip-dependency-check

echo.
echo Tests completed!
pause
