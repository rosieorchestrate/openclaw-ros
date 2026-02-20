#!/bin/bash
# demo_flow.sh - Demonstrate the full surveillance flow
# This script shows the complete pipeline: camera -> detection -> email

set -e

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
CAPTURE_DIR="$PROJECT_DIR/captures"
LOG_DIR="$PROJECT_DIR/logs"

echo "========================================="
echo "SURVEILLANCE SYSTEM FLOW DEMO"
echo "========================================="
echo ""
echo "This demo shows the complete flow:"
echo "  1. Camera feed → /camera/image_raw"
echo "  2. Detection node → 1Hz person detection"
echo "  3. Email node → Mock email + log"
echo ""
echo "Press Ctrl+C to stop at any time"
echo "========================================="
echo ""

# Source ROS2
source /opt/ros/kilted/setup.bash

# Clean previous captures/logs
echo "🧹 Cleaning previous captures and logs..."
rm -f "$CAPTURE_DIR"/*.jpg 2>/dev/null || true
rm -f "$LOG_DIR"/*.log 2>/dev/null || true

# Create directories
mkdir -p "$CAPTURE_DIR" "$LOG_DIR"

echo ""
echo "📁 Capture directory: $CAPTURE_DIR"
echo "📁 Log directory: $LOG_DIR"
echo ""

# Start detection node in background
echo "🎬 Starting Detection Node..."
ros2 run detection_node detection_node &
DETECTION_PID=$!
sleep 2

# Start email node in background
echo "📧 Starting Email Node..."
ros2 run email_node email_node &
EMAIL_PID=$!
sleep 2

# Show available topics
echo ""
echo "📡 Available topics:"
ros2 topic list | grep -E "(camera|detection|email)" | sed 's/^/   /'
echo ""

# Run flow tester
echo "🧪 Running flow test (simulating camera feed with person detection)..."
echo "   This will publish 50 test frames with simulated persons"
echo ""

cd "$PROJECT_DIR"
timeout 15 python3 scripts/test_flow.py 2>&1 || true

echo ""
echo "========================================="
echo "DEMO RESULTS"
echo "========================================="
echo ""

# Check for detection captures
DETECTION_COUNT=$(ls -1 "$CAPTURE_DIR"/detection_*.jpg 2>/dev/null | wc -l)
if [ "$DETECTION_COUNT" -gt 0 ]; then
    echo "✅ Detections captured: $DETECTION_COUNT frame(s)"
    ls -la "$CAPTURE_DIR"/detection_*.jpg 2>/dev/null | tail -5
else
    echo "⚠️  No detection captures found"
fi

# Check for email logs
LOG_COUNT=$(ls -1 "$LOG_DIR"/mock_emails_*.log 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo ""
    echo "✅ Email logs created: $LOG_COUNT file(s)"
    LATEST_LOG=$(ls -t "$LOG_DIR"/mock_emails_*.log 2>/dev/null | head -1)
    echo "   Latest: $(basename "$LATEST_LOG")"
    echo ""
    echo "📧 Sample email content:"
    echo "   ---"
    head -20 "$LATEST_LOG" | sed 's/^/   /'
    echo "   ---"
else
    echo ""
    echo "⚠️  No email logs found"
fi

echo ""
echo "========================================="
echo "Cleaning up..."
echo "========================================="

# Cleanup
kill $DETECTION_PID 2>/dev/null || true
kill $EMAIL_PID 2>/dev/null || true
sleep 1

echo ""
echo "✅ Demo complete!"
echo ""
echo "Files generated:"
echo "  Captures: $CAPTURE_DIR"
echo "  Logs: $LOG_DIR"
echo ""
echo "To view a detection frame:"
echo "  ls -la $CAPTURE_DIR/"
echo ""
echo "To view full email log:"
echo "  cat $LOG_DIR/mock_emails_*.log"