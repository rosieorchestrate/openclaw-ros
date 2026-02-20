#!/bin/bash
# build_workspace.sh - Build the ROS2 workspace

set -e

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
WS_DIR="$PROJECT_DIR/ros2_ws"

echo "========================================="
echo "Building ROS2 Surveillance Workspace"
echo "========================================="
echo ""

# Source ROS2
source /opt/ros/kilted/setup.bash

echo "✅ ROS2 environment loaded"
echo ""

# Navigate to workspace
cd "$WS_DIR"

# Clean previous builds if requested
if [ "$1" == "clean" ]; then
    echo "🧹 Cleaning previous builds..."
    rm -rf build/ install/ log/
fi

# Build all packages
echo "🔨 Building packages..."
colcon build --symlink-install --packages-select \
    capture_service \
    detection_node \
    email_node \
    surveillance_bringup \
    2>&1 | tee build.log

echo ""
echo "✅ Build complete"
echo ""

# Source the workspace
echo "📦 Sourcing workspace..."
source install/setup.bash

echo ""
echo "📋 Available executables:"
ros2 pkg executables | grep -E "(detection_node|email_node|surveillance_bringup)"

echo ""
echo "========================================="
echo "Build Summary"
echo "========================================="
echo ""
echo "To run the system:"
echo "  1. Source workspace: source $WS_DIR/install/setup.bash"
echo "  2. Launch system:   ros2 launch surveillance_bringup surveillance.launch.py"
echo ""
echo "Or run nodes individually:"
echo "  - Camera:   ros2 run camera_ros camera_node"
echo "  - Detection: ros2 run detection_node detection_node"
echo "  - Email:     ros2 run email_node email_node"