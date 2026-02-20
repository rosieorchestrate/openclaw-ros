#!/usr/bin/env python3
"""
Generate test image for camera verification.
When real camera is available, this will be replaced with actual capture.
"""

import cv2
import numpy as np
import os
from datetime import datetime

def create_test_image():
    """Create a test pattern image simulating camera feed."""
    # Create 640x480 test pattern
    width, height = 640, 480
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Gradient background
    for i in range(height):
        image[i, :] = [
            int(50 + (i / height) * 100),   # R
            int(100 + (i / height) * 50),   # G
            int(150 - (i / height) * 50)    # B
        ]
    
    # Add grid pattern
    for x in range(0, width, 64):
        cv2.line(image, (x, 0), (x, height), (255, 255, 255), 1)
    for y in range(0, height, 48):
        cv2.line(image, (0, y), (width, y), (255, 255, 255), 1)
    
    # Add text
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(image, 'ROS2 Camera Test Pattern', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, timestamp, (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(image, 'Resolution: 640x480', (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(image, 'camera_ros node ready', (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
    
    # Add simulated "person" rectangle (for detection testing)
    center_x, center_y = width // 2, height // 2
    cv2.rectangle(image, 
                  (center_x - 60, center_y - 80),
                  (center_x + 60, center_y + 80),
                  (100, 100, 100), -1)
    cv2.rectangle(image,
                  (center_x - 60, center_y - 80),
                  (center_x + 60, center_y + 80),
                  (255, 255, 255), 2)
    cv2.circle(image, (center_x, center_y - 100), 30, (100, 100, 100), -1)
    cv2.putText(image, 'SIMULATED PERSON', (center_x - 80, center_y + 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    return image

def main():
    # Ensure captures directory exists
    project_dir = os.path.expanduser(
        '~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2'
    )
    capture_dir = os.path.join(project_dir, 'captures')
    os.makedirs(capture_dir, exist_ok=True)
    
    # Generate and save test image
    test_image = create_test_image()
    output_path = os.path.join(capture_dir, 'test_image.jpg')
    cv2.imwrite(output_path, test_image)
    
    print(f"✅ Test image generated: {output_path}")
    print(f"   Resolution: {test_image.shape[1]}x{test_image.shape[0]}")
    print("")
    print("This image simulates camera output with:")
    print("  - Test pattern (gradient + grid)")
    print("  - Simulated person for detection testing")
    print("")
    print("When running on Raspberry Pi with camera connected:")
    print("  1. Source ROS2: source /opt/ros/kilted/setup.bash")
    print("  2. Launch camera: ros2 run camera_ros camera_node")
    print("  3. Verify topic: ros2 topic hz /camera/image_raw")
    print("  4. View image: ros2 run rqt_image_view rqt_image_view")

if __name__ == '__main__':
    main()