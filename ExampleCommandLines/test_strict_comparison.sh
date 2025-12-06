#!/bin/bash
# Test: Strict Comparison Mode
# This configuration catches every possible difference (very sensitive)
# Uses detailed histogram with more bins for precise analysis

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
  --histogram-bins 512 \
  --histogram-gray-alpha 0.9 \
  --histogram-rgb-alpha 0.9 \
  --skip-dependency-check
