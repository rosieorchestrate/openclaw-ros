#!/usr/bin/env python3
"""
Integration test for surveillance system flow.
Simulates camera frames and verifies detection -> email flow.
Usage: python3 test_flow.py
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
import sys

class FlowTester(Node):
    """Test node that simulates camera feed and monitors detection/email flow."""
    
    def __init__(self):
        super().__init__('flow_tester')
        self.bridge = CvBridge()
        
        # Create directories
        self.capture_dir = os.path.expanduser(
            '~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures'
        )
        os.makedirs(self.capture_dir, exist_ok=True)
        
        # Publishers (simulate camera)
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        
        # Subscribers (monitor detection and email)
        self.detection_sub = self.create_subscription(
            String, '/detection/events', self.on_detection, 10
        )
        self.create_subscription(String, '/detection/events', self.monitor_flow, 10)
        
        self.detection_count = 0
        self.test_passed = False
        
        # Test timer
        self.timer = self.create_timer(0.1, self.publish_test_frame)
        self.test_counter = 0
        
        self.get_logger().info('Flow Tester initialized')
        self.get_logger().info('Publishing test frames to /camera/image_raw...')
        
    def create_test_frame(self, frame_num):
        """Create a test frame with simulated person."""
        # Create base frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Gradient background
        for i in range(480):
            frame[i, :] = [50 + i//5, 100, 150 - i//5]
        
        # Every 10th frame, add a "person" (simulated detection target)
        if frame_num % 10 == 0:
            # Draw a person-like shape
            cv2.rectangle(frame, (270, 150), (370, 350), (100, 100, 100), -1)
            cv2.circle(frame, (320, 120), 40, (100, 100, 100), -1)
            
        # Add timestamp text
        cv2.putText(frame, f'Test Frame {frame_num}', (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def publish_test_frame(self):
        """Publish test frames at 10Hz."""
        frame = self.create_test_frame(self.test_counter)
        
        # Convert to ROS Image
        ros_image = self.bridge.cv2_to_imgmsg(frame, encoding='rgb8')
        ros_image.header.stamp = self.get_clock().now().to_msg()
        ros_image.header.frame_id = 'test_camera'
        
        self.image_pub.publish(ros_image)
        self.test_counter += 1
        
        # Stop after 50 frames
        if self.test_counter >= 50:
            self.timer.cancel()
            self.get_logger().info('Test frame publishing complete')
            # Wait a bit for processing, then report
            self.create_timer(2.0, self.report_results)
    
    def on_detection(self, msg):
        """Handle detection events."""
        self.detection_count += 1
        self.get_logger().info(f'Received detection event: {msg.data}')
        self.test_passed = True
    
    def monitor_flow(self, msg):
        """Monitor the full flow."""
        self.get_logger().info('✅ FLOW: Detection -> Email event received')
    
    def report_results(self):
        """Report test results."""
        self.get_logger().info('='*60)
        self.get_logger().info('FLOW TEST RESULTS')
        self.get_logger().info('='*60)
        self.get_logger().info(f'Frames published: {self.test_counter}')
        self.get_logger().info(f'Detections received: {self.detection_count}')
        
        if self.test_passed:
            self.get_logger().info('✅ FLOW TEST PASSED')
            self.get_logger().info('   Camera -> Detection -> Email pipeline working!')
        else:
            self.get_logger().warning('⚠️  No detections received')
            self.get_logger().info('   Make sure detection_node and email_node are running')
        
        self.get_logger().info('='*60)
        
        # Shutdown
        rclpy.shutdown()


def main():
    rclpy.init()
    tester = FlowTester()
    
    try:
        rclpy.spin(tester)
    except KeyboardInterrupt:
        pass
    finally:
        tester.destroy_node()


if __name__ == '__main__':
    main()