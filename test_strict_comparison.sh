#!/bin/bash
# Test: Strict Comparison Mode
# This configuration catches every possible difference (very sensitive)

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --pixel-diff-threshold 0.001 \
  --pixel-change-threshold 1 \
  --ssim-threshold 0.99 \
  --diff-enhancement 10.0 \
  --skip-dependency-check
