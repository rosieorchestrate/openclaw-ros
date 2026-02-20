#!/bin/bash
# pi_integration_test.sh - Full integration test for Raspberry Pi
# Run this on the Pi with camera connected

set -e

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
CAPTURE_DIR="$PROJECT_DIR/captures"
LOG_DIR="$PROJECT_DIR/logs"
TEST_DURATION=30  # seconds

echo "========================================="
echo "PI INTEGRATION TEST"
echo "ROS2 Camera Surveillance System"
echo "========================================="
echo ""
echo "Test duration: ${TEST_DURATION}s"
echo "Expected: Person detection + email notification"
echo ""

# Source ROS2
source /opt/ros/kilted/setup.bash
source "$PROJECT_DIR/ros2_ws/install/setup.bash"

# Clean previous test artifacts
echo "🧹 Cleaning previous test files..."
rm -f "$CAPTURE_DIR"/detection_*.jpg "$CAPTURE_DIR"/test_*.jpg 2>/dev/null || true
rm -f "$LOG_DIR"/mock_emails_*.log 2>/dev/null || true
mkdir -p "$CAPTURE_DIR" "$LOG_DIR"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up processes..."
    kill $CAMERA_PID $DETECT_PID $EMAIL_PID 2>/dev/null || true
    sleep 2
}
trap cleanup EXIT

# Start camera node
echo ""
echo "📷 Starting camera_ros node..."
ros2 run camera_ros camera_node \
    --ros-args \
    -p width:=640 \
    -p height:=480 \
    -p format:=RGB888 \
    -p camera:=0 &
CAMERA_PID=$!
echo "   PID: $CAMERA_PID"
sleep 5

# Verify camera is publishing
echo ""
echo "📡 Checking camera topic..."
if ros2 topic list | grep -q "/camera/image_raw"; then
    echo "   ✅ Camera topic found"
    ros2 topic hz /camera/image_raw &
    HZ_PID=$!
    sleep 3
    kill $HZ_PID 2>/dev/null || true
else
    echo "   ❌ Camera topic NOT found - check camera connection"
    exit 1
fi

# Start detection node
echo ""
echo "🔍 Starting detection_node..."
ros2 run detection_node detection_node &
DETECT_PID=$!
echo "   PID: $DETECT_PID"
sleep 3

# Start email node
echo ""
echo "📧 Starting email_node..."
ros2 run email_node email_node &
EMAIL_PID=$!
echo "   PID: $EMAIL_PID"
sleep 3

# Show running nodes
echo ""
echo "📋 Running ROS2 nodes:"
ros2 node list | sed 's/^/   /'

# Show topics
echo ""
echo "📡 Active topics:"
ros2 topic list | grep -E "(camera|detection)" | sed 's/^/   /'

# Run test for specified duration
echo ""
echo "⏱️  Running integration test for ${TEST_DURATION}s..."
echo "   Wave at the camera to trigger detection!"
echo ""

for i in $(seq 1 $TEST_DURATION); do
    echo -ne "   Testing... $i/${TEST_DURATION}s \r"
    sleep 1
done
echo ""

# Check results
echo ""
echo "========================================="
echo "TEST RESULTS"
echo "========================================="
echo ""

# Check for detection captures
DETECTION_COUNT=$(ls -1 "$CAPTURE_DIR"/detection_*.jpg 2>/dev/null | wc -l)
if [ "$DETECTION_COUNT" -gt 0 ]; then
    echo "✅ Detections captured: $DETECTION_COUNT"
    ls -lh "$CAPTURE_DIR"/detection_*.jpg | tail -3 | awk '{print "   " $9 " (" $5 ")"}'
    
    # Show latest detection frame info
    LATEST_DETECTION=$(ls -t "$CAPTURE_DIR"/detection_*.jpg 2>/dev/null | head -1)
    echo ""
    echo "   Latest detection: $(basename "$LATEST_DETECTION")"
else
    echo "⚠️  No detections captured"
    echo "   (This may be normal if no person was in frame)"
fi

# Check for email logs
LOG_COUNT=$(ls -1 "$LOG_DIR"/mock_emails_*.log 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo ""
    echo "✅ Email logs created: $LOG_COUNT"
    LATEST_LOG=$(ls -t "$LOG_DIR"/mock_emails_*.log 2>/dev/null | head -1)
    echo "   Log file: $(basename "$LATEST_LOG")"
    
    # Count email entries in log
    EMAIL_COUNT=$(grep -c "MOCK EMAIL NOTIFICATION" "$LATEST_LOG" 2>/dev/null || echo "0")
    echo "   Email notifications: $EMAIL_COUNT"
    
    # Show latest email snippet
    if [ "$EMAIL_COUNT" -gt 0 ]; then
        echo ""
        echo "   📧 Latest email preview:"
        echo "   ---"
        grep -A5 "Persons detected:" "$LATEST_LOG" | tail -6 | sed 's/^/   /'
        echo "   ---"
    fi
else
    echo ""
    echo "⚠️  No email logs found"
fi

# Check capture service
echo ""
echo "📸 Testing capture service..."
if ros2 service list | grep -q "/capture_frame"; then
    echo "   ✅ Capture service available"
    
    # Trigger a manual capture
    echo "   Triggering manual capture..."
    ros2 service call /capture_frame std_srvs/srv/Trigger {}
    sleep 1
    
    CAPTURE_COUNT=$(ls -1 "$CAPTURE_DIR"/capture_*.jpg 2>/dev/null | wc -l)
    if [ "$CAPTURE_COUNT" -gt 0 ]; then
        echo "   ✅ Manual capture successful ($CAPTURE_COUNT captures)"
    fi
else
    echo "   ⚠️  Capture service not available"
fi

# Summary
echo ""
echo "========================================="
echo "SUMMARY"
echo "========================================="
echo ""

if [ "$DETECTION_COUNT" -gt 0 ] && [ "$LOG_COUNT" -gt 0 ]; then
    echo "✅ INTEGRATION TEST PASSED"
    echo ""
    echo "Flow verified:"
    echo "   Camera → Detection → Email"
    echo ""
    echo "Files generated:"
    echo "   Captures: $CAPTURE_DIR"
    echo "   Logs: $LOG_DIR"
elif [ "$DETECTION_COUNT" -eq 0 ] && [ "$LOG_COUNT" -eq 0 ]; then
    echo "⚠️  No detections during test period"
    echo ""
    echo "Possible reasons:"
    echo "   - No person in camera frame"
    echo "   - Camera not connected properly"
    echo "   - Detection threshold too high"
    echo ""
    echo "Try running longer test or check camera:"
    echo "   ros2 run rqt_image_view rqt_image_view"
else
    echo "⚠️  PARTIAL SUCCESS"
    echo ""
    echo "Some components working, check logs for details"
fi

echo ""
echo "Test complete!"
echo "========================================="