#!/bin/bash
# Test: With Auto-Open Report
# This demonstrates using the --open-report flag to auto-open results in browser

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --skip-dependency-check \
  --open-report
