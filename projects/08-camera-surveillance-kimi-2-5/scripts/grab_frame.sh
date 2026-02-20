#!/bin/bash
# Quick camera test tool - grabs a single frame

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CAPTURE_DIR="$PROJECT_DIR/captures"
mkdir -p "$CAPTURE_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$CAPTURE_DIR/test_$TIMESTAMP.jpg"

echo "📷 Capturing frame from imx219 camera..."
echo "   Output: $OUTPUT_FILE"

# Use libcamera cam utility for single capture
cam --camera 0 --capture=1 --file="$OUTPUT_FILE"

echo "✅ Frame captured successfully!"
echo "   File: $OUTPUT_FILE"
