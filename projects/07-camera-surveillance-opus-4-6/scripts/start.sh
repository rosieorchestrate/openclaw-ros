#!/bin/bash
# ============================================================
# Start Surveillance System
# ============================================================
# Usage: ./scripts/start.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🎥 Camera Surveillance System"
echo "=============================="
echo "Project root: $PROJECT_ROOT"
echo ""

# Source ROS2
source /opt/ros/kilted/setup.bash
echo "✅ ROS2 Kilted sourced"

# Check camera
echo "🔍 Checking camera..."
if cam --list 2>&1 | grep -q "Available cameras"; then
    echo "✅ Camera detected"
else
    echo "❌ No camera detected! Check connection."
    exit 1
fi

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/captures/detections"
mkdir -p "$PROJECT_ROOT/captures/snapshots"

echo ""
echo "🚀 Launching surveillance pipeline..."
echo "   Press Ctrl+C to stop all nodes"
echo ""

# Launch via ROS2 launch
cd "$PROJECT_ROOT"
ros2 launch launch/surveillance_launch.py
