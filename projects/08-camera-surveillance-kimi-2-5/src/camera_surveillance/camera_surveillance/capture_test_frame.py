#!/usr/bin/env python3
"""
Test Frame Capture Tool

Captures a single frame from the camera stream and saves it.
Can be triggered via terminal while surveillance is running.

Usage:
  ros2 run camera_surveillance capture_test_frame
  OR
  python3 scripts/capture_test_frame.py
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from datetime import datetime
from pathlib import Path
import sys


class TestFrameCapture(Node):
    """Capture a single test frame from camera stream."""
    
    def __init__(self):
        super().__init__('test_frame_capture')
        
        # Get capture directory from parameter or use default
        self.declare_parameter('capture_dir', 'captures')
        capture_dir = self.get_parameter('capture_dir').value
        
        # Resolve path
        if capture_dir == 'captures':
            # Default to project captures directory
            project_dir = Path(__file__).parent.parent.parent.parent
            self.capture_dir = project_dir / 'captures'
        else:
            self.capture_dir = Path(capture_dir)
        
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        
        self.get_logger().info('📷 Test Frame Capture Tool')
        self.get_logger().info(f'   Capture dir: {self.capture_dir}')
        
        # CV Bridge
        self.bridge = CvBridge()
        self.frame_captured = False
        
        # Subscribe to camera topic (using /camera_ros/image_raw as published by camera_ros)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        self.image_sub = self.create_subscription(
            Image, '/camera_ros/image_raw', self.image_callback, qos_profile
        )
        
        self.get_logger().info('   Waiting for frame on /camera_ros/image_raw...')
    
    def image_callback(self, msg: Image):
        """Capture first frame and save."""
        if self.frame_captured:
            return
        
        try:
            # Convert ROS Image to OpenCV
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'test_frame_{timestamp}.jpg'
            filepath = self.capture_dir / filename
            
            # Save frame
            cv2.imwrite(str(filepath), frame)
            self.frame_captured = True
            
            self.get_logger().info('✅ Test frame captured!')
            self.get_logger().info(f'   Saved: {filepath}')
            self.get_logger().info(f'   Resolution: {frame.shape[1]}x{frame.shape[0]}')
            
            # Shutdown after capture
            self.get_logger().info('   Exiting...')
            rclpy.shutdown()
            
        except Exception as e:
            self.get_logger().error(f'Failed to capture frame: {e}')


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = TestFrameCapture()
        
        # Spin until frame captured (max 30 seconds)
        start_time = node.get_clock().now().seconds_nanoseconds()[0]
        while rclpy.ok() and not node.frame_captured:
            rclpy.spin_once(node, timeout_sec=1.0)
            
            # Check timeout
            current_time = node.get_clock().now().seconds_nanoseconds()[0]
            if current_time - start_time > 30:
                node.get_logger().error('Timeout: No frame received within 30 seconds')
                break
        
        node.destroy_node()
        
        if node.frame_captured:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
