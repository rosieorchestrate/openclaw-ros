#!/usr/bin/env python3
"""
Capture a single frame from camera_ros topic and save to file.
Usage: python3 capture_frame.py
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import signal
import sys

class FrameCapture(Node):
    def __init__(self):
        super().__init__('frame_capture')
        self.bridge = CvBridge()
        self.captured = False
        
        # Create capture directory
        self.capture_dir = os.path.expanduser(
            '~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures'
        )
        os.makedirs(self.capture_dir, exist_ok=True)
        
        # Subscribe to camera topic
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        self.get_logger().info('Waiting for frames on /camera/image_raw...')
    
    def image_callback(self, msg):
        if self.captured:
            return
        
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'rgb8')
            
            # Save frame
            output_path = os.path.join(self.capture_dir, 'captured_frame.jpg')
            cv2.imwrite(output_path, cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR))
            
            self.get_logger().info(f'✅ Frame captured: {output_path}')
            self.get_logger().info(f'   Resolution: {cv_image.shape[1]}x{cv_image.shape[0]}')
            self.get_logger().info(f'   Encoding: {msg.encoding}')
            
            self.captured = True
            
        except Exception as e:
            self.get_logger().error(f'Failed to capture: {e}')

def main():
    rclpy.init()
    node = FrameCapture()
    
    # Capture single frame then exit
    timeout = 15.0  # seconds
    start_time = node.get_clock().now()
    
    while rclpy.ok() and not node.captured:
        rclpy.spin_once(node, timeout_sec=0.1)
        elapsed = (node.get_clock().now() - start_time).nanoseconds / 1e9
        if elapsed > timeout:
            node.get_logger().error('⏱️ Timeout: No frames received within 15s')
            break
    
    if node.captured:
        node.get_logger().info('Capture successful!')
    else:
        node.get_logger().error('Capture failed - check camera connection')
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()