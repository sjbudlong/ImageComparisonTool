@echo off
REM Test: 3D Rendering Mode Comparison
REM This demonstrates comparison with histogram equalization for 3D renders

cd /d "%~dp0"
cd ImageComparisonSystem

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --use-histogram-eq ^
  --color-distance-threshold 20.0 ^
  --min-contour-area 100 ^
  --highlight-color "0,0,255" ^
  --skip-dependency-check

pause
