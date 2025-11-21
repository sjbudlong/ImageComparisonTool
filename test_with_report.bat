@echo off
REM Test: With Auto-Open Report
REM This demonstrates using the --open-report flag to auto-open results in browser

cd /d "%~dp0"
cd ImageComparisonSystem

python main.py ^
  --base-dir ../examples ^
  --new-dir new ^
  --known-good-dir known_good ^
  --skip-dependency-check ^
  --open-report

pause
