#!/bin/bash
# Test: Basic CLI Mode Comparison
# This demonstrates the simplest command-line usage of the Image Comparison Tool

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --skip-dependency-check
