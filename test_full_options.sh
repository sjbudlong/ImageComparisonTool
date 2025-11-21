#!/bin/bash
# Test: Full Options Comparison
# This demonstrates all available command-line options

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --diff-dir diffs \
  --html-dir reports \
  --pixel-diff-threshold 0.01 \
  --pixel-change-threshold 1 \
  --ssim-threshold 0.95 \
  --color-distance-threshold 10.0 \
  --min-contour-area 50 \
  --use-histogram-eq \
  --highlight-color "255,0,0" \
  --diff-enhancement 5.0 \
  --skip-dependency-check
