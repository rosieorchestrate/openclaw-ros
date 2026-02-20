# Copyright 2025 Noah Ploch, Jakub Skupien
# SPDX-License-Identifier: MIT

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

# Try picamera2 first (libcamera), fallback to cv2.VideoCapture
PICAMERA_AVAILABLE = False
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    pass


class CameraPublisher(Node):
    """
    ROS2 Camera Node using libcamera (Picamera2) for Raspberry Pi.
    Publishes images to /camera/image_raw at configurable frame rate.
    """

    def __init__(self):
        super().__init__('camera_publisher')
        
        # Parameters
        self.declare_parameter('frame_rate', 10.0)
        self.declare_parameter('resolution_width', 640)
        self.declare_parameter('resolution_height', 480)
        self.declare_parameter('use_picamera', True)
        
        self.frame_rate = self.get_parameter('frame_rate').value
        self.width = self.get_parameter('resolution_width').value
        self.height = self.get_parameter('resolution_height').value
        self.use_picamera = self.get_parameter('use_picamera').value and PICAMERA_AVAILABLE
        
        # Publisher
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()
        
        # Timer for publishing
        timer_period = 1.0 / self.frame_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # Initialize camera
        self.camera = None
        self._init_camera()
        
        self.get_logger().info(
            f'CameraPublisher initialized: {self.width}x{self.height} @ {self.frame_rate}Hz '
            f'({"Picamera2" if self.use_picamera else "OpenCV"})'
        )

    def _init_camera(self):
        """Initialize camera based on availability."""
        try:
            if self.use_picamera:
                self.get_logger().info('Initializing Picamera2 (libcamera)...')
                self.camera = Picamera2()
                config = self.camera.create_preview_configuration(
                    main={'size': (self.width, self.height), 'format': 'RGB888'}
                )
                self.camera.configure(config)
                self.camera.start()
                self.get_logger().info('Picamera2 initialized successfully')
            else:
                self.get_logger().info('Initializing OpenCV VideoCapture...')
                self.camera = cv2.VideoCapture(0)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.get_logger().info('OpenCV VideoCapture initialized')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize camera: {e}')
            raise

    def timer_callback(self):
        """Capture and publish frame."""
        try:
            if self.use_picamera:
                frame = self.camera.capture_array()
            else:
                ret, frame = self.camera.read()
                if not ret:
                    self.get_logger().warning('Failed to capture frame')
                    return
            
            # Convert to ROS Image message
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding='rgb8')
            ros_image.header.stamp = self.get_clock().now().to_msg()
            ros_image.header.frame_id = 'camera_frame'
            
            self.publisher.publish(ros_image)
            
        except Exception as e:
            self.get_logger().error(f'Error in capture/publish: {e}')

    def destroy_node(self):
        """Cleanup camera resources."""
        if self.camera:
            if self.use_picamera:
                self.camera.stop()
            else:
                self.camera.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Camera node stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()