#!/usr/bin/env python3
"""
ROS2 Capture Server Node
Provides on-demand frame capture via ROS2 service while surveillance is running.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from datetime import datetime
from std_srvs.srv import Trigger
from rclpy.qos import qos_profile_sensor_data


class CaptureServer(Node):
    """
    Capture Server - Listens to camera topic and captures frames on demand.
    
    Services:
        /capture_frame (std_srvs/srv/Trigger) - Capture current frame
        /capture_start_continuous (std_srvs/srv/Trigger) - Start 1Hz capture
        /capture_stop_continuous (std_srvs/srv/Trigger) - Stop continuous capture
    """

    def __init__(self):
        super().__init__('capture_server')
        
        # Parameters
        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('output_dir', os.path.expanduser(
            '~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures'
        ))
        self.declare_parameter('continuous_rate', 1.0)
        
        self.input_topic = self.get_parameter('input_topic').value
        self.output_dir = self.get_parameter('output_dir').value
        self.continuous_rate = self.get_parameter('continuous_rate').value
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Latest frame storage
        self.latest_frame = None
        self.latest_header = None
        self.bridge = CvBridge()
        
        # Subscription to camera topic
        self.subscription = self.create_subscription(
            Image,
            self.input_topic,
            self.image_callback,
            qos_profile=qos_profile_sensor_data
        )
        
        # Services
        self.capture_service = self.create_service(
            Trigger, '/capture_frame', self.capture_frame_callback
        )
        self.start_continuous_service = self.create_service(
            Trigger, '/capture_start_continuous', self.start_continuous_callback
        )
        self.stop_continuous_service = self.create_service(
            Trigger, '/capture_stop_continuous', self.stop_continuous_callback
        )
        
        # Continuous capture timer
        self.continuous_timer = None
        
        self.get_logger().info(f'CaptureServer initialized')
        self.get_logger().info(f'  Input: {self.input_topic}')
        self.get_logger().info(f'  Output: {self.output_dir}')
        self.get_logger().info(f'  Services: /capture_frame, /capture_start_continuous, /capture_stop_continuous')

    def image_callback(self, msg):
        """Store latest frame."""
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, 'rgb8')
            self.latest_header = msg.header
        except Exception as e:
            self.get_logger().error(f'Error converting image: {e}')

    def save_frame(self, prefix='manual'):
        """Save the current latest frame."""
        if self.latest_frame is None:
            return False, 'No frame available yet'
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f'{prefix}_{timestamp}.jpg'
            filepath = os.path.join(self.output_dir, filename)
            
            # Convert RGB to BGR for OpenCV
            bgr_frame = cv2.cvtColor(self.latest_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filepath, bgr_frame)
            
            msg = f'Saved: {filename} ({self.latest_frame.shape[1]}x{self.latest_frame.shape[0]})'
            self.get_logger().info(msg)
            return True, msg
            
        except Exception as e:
            error_msg = f'Error saving frame: {str(e)}'
            self.get_logger().error(error_msg)
            return False, error_msg

    def capture_frame_callback(self, request, response):
        """Service handler for single frame capture."""
        success, message = self.save_frame(prefix='capture')
        response.success = success
        response.message = message
        return response

    def start_continuous_callback(self, request, response):
        """Start continuous capture at configured rate."""
        if self.continuous_timer is not None:
            response.success = False
            response.message = 'Continuous capture already running'
            return response
        
        period = 1.0 / self.continuous_rate
        self.continuous_timer = self.create_timer(period, self.continuous_capture_callback)
        
        msg = f'Started continuous capture at {self.continuous_rate}Hz'
        self.get_logger().info(msg)
        response.success = True
        response.message = msg
        return response

    def stop_continuous_callback(self, request, response):
        """Stop continuous capture."""
        if self.continuous_timer is None:
            response.success = False
            response.message = 'Continuous capture not running'
            return response
        
        self.continuous_timer.cancel()
        self.continuous_timer = None
        
        msg = 'Stopped continuous capture'
        self.get_logger().info(msg)
        response.success = True
        response.message = msg
        return response

    def continuous_capture_callback(self):
        """Timer callback for continuous capture."""
        self.save_frame(prefix='continuous')


def main(args=None):
    rclpy.init(args=args)
    node = CaptureServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Capture server stopped')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()