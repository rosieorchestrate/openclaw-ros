#!/usr/bin/env python3
"""
Camera Capture Node

Captures frames from libcamera-compatible camera at 1 Hz
and publishes as ROS2 Image messages.

Rosie Robotics - Reflective Discovery Principle:
- Verify camera exists before initialization
- Log all operations for debugging
- Graceful degradation on errors
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import subprocess
import tempfile
import os
from datetime import datetime


class CameraNode(Node):
    """ROS2 Node for camera frame capture using libcamera."""
    
    def __init__(self):
        super().__init__('camera_node')
        
        # Parameters
        self.declare_parameter('capture_rate_hz', 1.0)
        self.declare_parameter('camera_index', 0)
        self.declare_parameter('frame_width', 640)
        self.declare_parameter('frame_height', 480)
        
        self.capture_rate = self.get_parameter('capture_rate_hz').value
        self.camera_index = self.get_parameter('camera_index').value
        self.frame_width = self.get_parameter('frame_width').value
        self.frame_height = self.get_parameter('frame_height').value
        
        # Logging
        self.get_logger().info(f'🎥 Camera Node initializing...')
        self.get_logger().info(f'   Rate: {self.capture_rate} Hz')
        self.get_logger().info(f'   Resolution: {self.frame_width}x{self.frame_height}')
        
        # Verify camera exists (Reflective Discovery)
        if not self._verify_camera():
            self.get_logger().error('❌ No camera detected! Check connections.')
            raise RuntimeError('Camera verification failed')
        
        # ROS2 Publisher
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.image_pub = self.create_publisher(Image, 'camera/image_raw', qos_profile)
        
        # CV Bridge
        self.bridge = CvBridge()
        
        # Timer for periodic capture (1 Hz to avoid hardware overload)
        timer_period = 1.0 / self.capture_rate
        self.timer = self.create_timer(timer_period, self.capture_callback)
        
        # Stats
        self.frame_count = 0
        self.error_count = 0
        
        self.get_logger().info('✅ Camera Node ready and publishing to /camera/image_raw')
    
    def _verify_camera(self) -> bool:
        """Verify camera is accessible via libcamera."""
        try:
            result = subprocess.run(
                ['cam', '--list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and 'imx219' in result.stdout:
                self.get_logger().info('✓ Camera verified: imx219 detected')
                return True
            return False
        except Exception as e:
            self.get_logger().warning(f'Camera verification warning: {e}')
            # Continue anyway - camera might work
            return True
    
    def capture_callback(self):
        """Capture a single frame and publish."""
        try:
            # Use libcamera cam utility for capture
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Capture via cam CLI (most reliable on Raspberry Pi)
            # Camera index adjustment: libcamera uses 1-based index
            cam_idx = 1 if self.camera_index == 0 else self.camera_index
            cmd = [
                'cam',
                '--camera', str(cam_idx),
                '--capture=1',
                '--file=' + tmp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode != 0:
                self.error_count += 1
                self.get_logger().warning(f'Capture failed: {result.stderr.decode()}')
                return
            
            # Read captured image
            frame = cv2.imread(tmp_path)
            os.unlink(tmp_path)  # Clean up temp file
            
            if frame is None:
                self.error_count += 1
                self.get_logger().warning('Failed to read captured frame')
                return
            
            # Resize if needed
            if frame.shape[1] != self.frame_width or frame.shape[0] != self.frame_height:
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            
            # Convert to ROS2 Image message
            image_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            image_msg.header.stamp = self.get_clock().now().to_msg()
            image_msg.header.frame_id = 'camera_frame'
            
            # Publish
            self.image_pub.publish(image_msg)
            self.frame_count += 1
            
            # Log every 10 frames
            if self.frame_count % 10 == 0:
                self.get_logger().info(f'📷 Frames captured: {self.frame_count}')
            
        except subprocess.TimeoutExpired:
            self.error_count += 1
            self.get_logger().warning('Capture timeout')
        except Exception as e:
            self.error_count += 1
            self.get_logger().error(f'Capture error: {str(e)}')
    
    def get_status(self) -> dict:
        """Return current node status for diagnostics."""
        return {
            'frames_captured': self.frame_count,
            'errors': self.error_count,
            'capture_rate_hz': self.capture_rate,
            'resolution': f'{self.frame_width}x{self.frame_height}'
        }


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = CameraNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Camera Node failed: {e}')
    finally:
        if 'node' in locals():
            node.get_logger().info(f'📊 Final stats: {node.get_status()}')
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
