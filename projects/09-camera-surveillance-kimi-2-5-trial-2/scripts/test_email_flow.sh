#!/bin/bash
# test_email_flow.sh - Simulate detection events to test email node without camera

set -e

source /opt/ros/kilted/setup.bash

echo "========================================="
echo "EMAIL FLOW TEST"
echo "========================================="
echo ""
echo "This test simulates detection events to verify"
echo "the email node processes them correctly."
echo ""

# Ensure directories exist
PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
mkdir -p "$PROJECT_DIR/captures" "$PROJECT_DIR/logs"

# Create a fake detection image
python3 << 'PYEOF'
import cv2
import numpy as np
import os
from datetime import datetime

project_dir = os.path.expanduser(
    '~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2'
)
capture_dir = os.path.join(project_dir, 'captures')
os.makedirs(capture_dir, exist_ok=True)

# Create test image with simulated detection
frame = np.zeros((480, 640, 3), dtype=np.uint8)
frame[:] = [100, 150, 200]  # Blue background

# Draw bounding box (simulated person detection)
cv2.rectangle(frame, (200, 100), (400, 400), (0, 255, 0), 3)
cv2.putText(frame, 'Person: 0.87', (200, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# Add timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'detection_{timestamp}.jpg'
filepath = os.path.join(capture_dir, filename)
cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

print(f"✅ Created test detection image: {filename}")
print(f"   Path: {filepath}")
PYEOF

echo ""
echo "📧 Starting email node..."
echo "   (Will process simulated detection in 3 seconds)"
echo ""

# Start email node in background
ros2 run email_node email_node &
EMAIL_PID=$!
sleep 2

echo "📡 Publishing simulated detection event..."
echo ""

# Publish a simulated detection event
cat << 'ROSEOF' | ros2 topic pub --once /detection/events std_msgs/msg/String "data: '$(cat)'" 2>&1 | head -5 || true
{'timestamp': '2025-02-17T18:20:00.000000', 'filename': 'detection_20250217_182000.jpg', 'path': '/home/opencw/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures/detection_20250217_182000.jpg', 'person_count': 1, 'confidences': [0.87]}
ROSEOF

# Alternative direct publish
ros2 topic pub --once /detection/events std_msgs/msg/String '{data: "{\"timestamp\": \"2025-02-17T18:20:00\", \"filename\": \"detection_test.jpg\", \"path\": \"/home/opencw/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures/detection_test.jpg\", \"person_count\": 1, \"confidences\": [0.87]}"}' &

sleep 3

echo ""
echo "========================================="
echo "Checking results..."
echo "========================================="
echo ""

# Check for email log
LOG_DIR="$PROJECT_DIR/logs"
LOG_COUNT=$(ls -1 "$LOG_DIR"/mock_emails_*.log 2>/dev/null | wc -l)

if [ "$LOG_COUNT" -gt 0 ]; then
    echo "✅ Email log created successfully"
    LATEST_LOG=$(ls -t "$LOG_DIR"/mock_emails_*.log 2>/dev/null | head -1)
    echo ""
    echo "📧 Email content preview:"
    echo "---"
    head -25 "$LATEST_LOG" | sed 's/^/  /'
    echo "---"
else
    echo "⚠️  No email log found"
fi

echo ""
echo "🧹 Cleaning up..."
kill $EMAIL_PID 2>/dev/null || true

echo ""
echo "✅ Test complete!"
echo ""
echo "To see full email log:"
echo "  cat $LOG_DIR/mock_emails_*.log"