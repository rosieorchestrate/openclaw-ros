#!/usr/bin/env python3
"""
Snapshot Node — Quick Camera Capture via CLI
Subscribes to /camera/image_raw, waits for a single frame,
saves it to captures/snapshots/, and exits.

Usage:
  bash scripts/snapshot.sh
  # or directly:
  ros2 run ... snapshot_node --ros-args -p project_root:=/path/to/project
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import cv2
import os
import time
from datetime import datetime


class SnapshotNode(Node):
    def __init__(self):
        super().__init__('snapshot_node')

        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('project_root', '')
        self.declare_parameter('output_name', '')  # Optional custom filename

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.project_root = self.get_parameter('project_root').get_parameter_value().string_value
        self.output_name = self.get_parameter('output_name').get_parameter_value().string_value

        # Ensure snapshots directory
        self.snapshots_dir = os.path.join(self.project_root, 'captures', 'snapshots')
        os.makedirs(self.snapshots_dir, exist_ok=True)

        self.bridge = CvBridge()
        self.captured = False

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            Image,
            input_topic,
            self.image_callback,
            sensor_qos
        )

        self.get_logger().info(f'Snapshot Node waiting for frame on {input_topic}...')

    def image_callback(self, msg: Image):
        if self.captured:
            return

        self.captured = True

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            rclpy.shutdown()
            return

        # Generate filename
        if self.output_name:
            filename = self.output_name
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'snapshot_{timestamp}.jpg'

        filepath = os.path.join(self.snapshots_dir, filename)
        cv2.imwrite(filepath, cv_image)

        (h, w) = cv_image.shape[:2]
        self.get_logger().info(f'📸 Snapshot saved: {filepath} ({w}x{h})')
        print(f'\n✅ Snapshot saved: {filepath} ({w}x{h})\n')

        # Exit after capture
        raise SystemExit(0)


def main(args=None):
    rclpy.init(args=args)
    node = SnapshotNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
