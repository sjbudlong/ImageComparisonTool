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

pause
