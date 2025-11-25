#!/bin/bash
# Test: Lenient Comparison Mode
# This configuration only flags major changes (less sensitive)
# Uses smoother histogram with fewer bins for overview

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --pixel-diff-threshold 1.0 \
  --pixel-change-threshold 5 \
  --ssim-threshold 0.90 \
  --histogram-bins 64 \
  --histogram-gray-alpha 0.7 \
  --histogram-rgb-alpha 0.7 \
  --skip-dependency-check
