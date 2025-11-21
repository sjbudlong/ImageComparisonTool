#!/bin/bash
# Test: Lenient Comparison Mode
# This configuration only flags major changes (less sensitive)

cd "$(dirname "$0")"
cd ImageComparisonSystem

python main.py \
  --base-dir ../examples \
  --new-dir new \
  --known-good-dir known_good \
  --pixel-diff-threshold 1.0 \
  --pixel-change-threshold 5 \
  --ssim-threshold 0.90 \
  --skip-dependency-check
