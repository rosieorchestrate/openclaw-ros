#!/bin/bash
# deploy_and_verify.sh - Deploy camera_ros and verify frame capture

set -e

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
CAPTURE_DIR="$PROJECT_DIR/captures"
LOG_FILE="$PROJECT_DIR/logs/camera_verify.log"

mkdir -p "$CAPTURE_DIR" "$PROJECT_DIR/logs"

echo "========================================="
echo "Camera ROS2 Deployment & Verification"
echo "========================================="
echo ""

# Source ROS2 (using bash)
source /opt/ros/kilted/setup.bash

echo "✅ ROS2 environment loaded"
echo "   Distro: $(ros2 --version 2>&1 | head -1)"
echo ""

# Check camera_ros availability
if ! ros2 pkg list | grep -q "^camera_ros$"; then
    echo "❌ camera_ros package not found"
    exit 1
fi
echo "✅ camera_ros package available"

# Start camera node
echo ""
echo "🎥 Starting camera_ros node..."
echo "   Resolution: 640x480"
echo "   Format: RGB888"
echo "   Topic: /camera/image_raw"
echo ""

ros2 run camera_ros camera_node --ros-args \
    -p width:=640 \
    -p height:=480 \
    -p format:=RGB888 \
    -p camera:=0 \
    2>&1 | tee "$LOG_FILE" &

CAMERA_PID=$!
echo "   Camera node PID: $CAMERA_PID"

# Wait for initialization
sleep 3

# Check topics
echo ""
echo "📡 Checking ROS2 topics..."
echo "   Available topics:"
ros2 topic list | sed 's/^/     - /'

echo ""
if ros2 topic list | grep -q "/camera/image_raw"; then
    echo "✅ Camera topic found: /camera/image_raw"
    
    echo ""
    echo "📊 Topic information:"
    ros2 topic info /camera/image_raw | sed 's/^/   /'
    
    echo ""
    echo "📸 Attempting frame capture..."
    cd "$PROJECT_DIR"
    timeout 10 python3 scripts/capture_frame.py 2>&1 | tee -a "$LOG_FILE"
    
    # Check if capture succeeded
    if [ -f "$CAPTURE_DIR/captured_frame.jpg" ]; then
        echo ""
        echo "✅ CAPTURE SUCCESSFUL"
        echo "   Frame saved: captures/captured_frame.jpg"
        ls -lh "$CAPTURE_DIR/captured_frame.jpg" | awk '{print "   Size: " $5}'
    else
        echo ""
        echo "⚠️  Capture incomplete - check logs"
    fi
else
    echo "❌ Camera topic NOT found"
    echo "   Check camera connection and libcamera setup"
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $CAMERA_PID 2>/dev/null || true
sleep 1

echo ""
echo "========================================="
echo "Verification complete"
echo "Log: logs/camera_verify.log"
echo "=========================================