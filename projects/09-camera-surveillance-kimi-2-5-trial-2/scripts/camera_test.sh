#!/bin/bash
# camera_test.sh - Test camera_ros with test pattern or live camera

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"
CAPTURE_DIR="$PROJECT_DIR/captures"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$CAPTURE_DIR" "$LOG_DIR"

# Source ROS2
source /opt/ros/kilted/setup.bash 2>/dev/null || {
    echo "ERROR: Could not source ROS2"
    exit 1
}

# Check if camera is available
if libcamera-still --list 2>/dev/null | grep -q "Available cameras"; then
    echo "✅ Camera detected - running live test"
    MODE="live"
else
    echo "⚠️  No camera detected - using test pattern"
    MODE="test"
fi

# Run camera_ros with appropriate mode
if [ "$MODE" = "test" ]; then
    # Test pattern mode for validation
    ros2 run camera_ros camera_node --ros-args \
        -p width:=640 \
        -p height:=480 \
        -p format:=RGB888 \
        -p test_pattern:=1 \
        -p camera:=0 &
else
    # Live camera mode
    ros2 run camera_ros camera_node --ros-args \
        -p width:=640 \
        -p height:=480 \
        -p format:=RGB888 &
fi

CAMERA_PID=$!
echo "Camera node started (PID: $CAMERA_PID)"

# Wait for topic to be available
echo "Waiting for /camera/image_raw topic..."
sleep 2

# Capture a frame using ros2 topic echo + Python conversion
timeout 5 ros2 topic echo --once /camera/image_raw > /tmp/camera_frame.txt 2>&1

if [ -s /tmp/camera_frame.txt ]; then
    echo "✅ Camera topic is publishing"
    python3 << 'PYEOF'
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

rclpy.init()
node = Node('capture_node')
bridge = CvBridge()
captured = False

def callback(msg):
    global captured
    if not captured:
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, 'rgb8')
            save_path = os.path.expanduser(
                '~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures/test_image.jpg'
            )
            cv2.imwrite(save_path, cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR))
            print(f"📸 Test image saved to: {save_path}")
            print(f"   Resolution: {cv_image.shape[1]}x{cv_image.shape[0]}")
            captured = True
        except Exception as e:
            print(f"Error: {e}")

sub = node.create_subscription(Image, '/camera/image_raw', callback, 10)

# Wait for capture
timeout = 10
import time
start = time.time()
while not captured and time.time() - start < timeout:
    rclpy.spin_once(node, timeout_sec=0.1)

node.destroy_node()
rclpy.shutdown()

if captured:
    print("✅ Camera test PASSED")
else:
    print("❌ Camera test FAILED - no frame captured")
PYEOF
else
    echo "❌ Camera topic not publishing"
fi

# Cleanup
kill $CAMERA_PID 2>/dev/null

echo ""
echo "Test complete. Check $CAPTURE_DIR/test_image.jpg"