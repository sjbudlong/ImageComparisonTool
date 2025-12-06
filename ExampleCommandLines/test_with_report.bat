@echo off
REM Test: With Auto-Open Report
REM This demonstrates using the --open-report flag to auto-open results in browser
REM Histogram configured for good visibility in browser display

cd /d "%~dp0"
cd ImageComparisonSystem

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --histogram-bins 256 ^
  --histogram-width 16 ^
  --histogram-height 6 ^
  --skip-dependency-check ^
  --open-report

pause
