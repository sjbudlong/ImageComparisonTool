#!/bin/bash
# Test: With Auto-Open Report
# This demonstrates using the --open-report flag to auto-open results in browser
# Histogram configured for good visibility in browser display

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --histogram-bins 256 \
  --histogram-width 16 \
  --histogram-height 6 \
  --skip-dependency-check \
  --open-report
