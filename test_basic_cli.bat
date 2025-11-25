@echo off
REM Test: Basic CLI Mode Comparison
REM This demonstrates the simplest command-line usage of the Image Comparison Tool

cd /d "%~dp0"
cd ImageComparisonSystem

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --skip-dependency-check

REM NOTE: Histogram configuration is now available via:
REM   --histogram-bins 256 (64-512)
REM   --histogram-width 16 (figure width in inches)
REM   --histogram-height 6 (figure height in inches)
REM   --histogram-gray-alpha 0.7 (grayscale transparency)
REM   --histogram-rgb-alpha 0.7 (RGB transparency)
REM   --histogram-gray-linewidth 2.0
REM   --histogram-rgb-linewidth 1.5
REM   --show-grayscale (show grayscale histogram)
REM   --show-rgb (show RGB histograms)
REM See test_histogram_config.bat for examples

pause
