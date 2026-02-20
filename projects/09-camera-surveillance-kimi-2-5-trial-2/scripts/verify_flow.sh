#!/bin/bash
# verify_flow.sh - Direct flow verification

set -e

source /opt/ros/kilted/setup.bash
source ~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/ros2_ws/install/setup.bash

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
cd "$PROJECT_DIR"

# Clean up
rm -f captures/*.jpg logs/*.log 2>/dev/null
mkdir -p captures logs

echo "========================================="
echo "FLOW VERIFICATION TEST"
echo "========================================="
echo ""

# Check executables
echo "1. Checking executables..."
which detection_node && echo "   ✅ detection_node" || echo "   ❌ detection_node not found"
which email_node && echo "   ✅ email_node" || echo "   ❌ email_node not found"
which capture_server && echo "   ✅ capture_server" || echo "   ❌ capture_server not found"
echo ""

# Start detection node
echo "2. Starting detection_node..."
ros2 run detection_node detection_node > logs/detection.log 2>&1 &
DETPID=$!
echo "   PID: $DETPID"
sleep 3

# Start email node
echo "3. Starting email_node..."
ros2 run email_node email_node > logs/email.log 2>&1 &
EMAILPID=$!
echo "   PID: $EMAILPID"
sleep 3

# Check topics
echo ""
echo "4. Checking ROS2 topics..."
ros2 topic list | grep -E "(camera|detection)" | sed 's/^/   /'
echo ""

# Publish a test detection event directly
echo "5. Publishing test detection event..."
ros2 topic pub --once /detection/events std_msgs/msg/String "{data: '{\"timestamp\": \"2025-02-17T18:00:00\", \"filename\": \"test_detection.jpg\", \"path\": \"/home/opencw/captures/test_detection.jpg\", \"person_count\": 1, \"confidences\": [0.85]}'" &
sleep 2

# Show email node output
echo ""
echo "6. Email node output:"
echo "   ---"
tail -30 logs/email.log 2>/dev/null | sed 's/^/   /' || echo "   (no output yet)"
echo "   ---"

# Cleanup
echo ""
echo "7. Cleaning up..."
kill $DETPID $EMAILPID 2>/dev/null || true
sleep 1

# Check logs
echo ""
echo "8. Log files created:"
ls -la logs/ 2>/dev/null | sed 's/^/   /'

echo ""
echo "========================================="
echo "Verification complete"
echo "========================================="