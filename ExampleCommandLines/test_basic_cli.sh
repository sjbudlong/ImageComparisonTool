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

# NOTE: Histogram configuration is now available via:
#   --histogram-bins 256 (64-512)
#   --histogram-width 16 (figure width in inches)
#   --histogram-height 6 (figure height in inches)
#   --histogram-gray-alpha 0.7 (grayscale transparency)
#   --histogram-rgb-alpha 0.7 (RGB transparency)
#   --histogram-gray-linewidth 2.0
#   --histogram-rgb-linewidth 1.5
#   --show-grayscale (show grayscale histogram)
#   --show-rgb (show RGB histograms)
# See test_histogram_config.sh for examples
