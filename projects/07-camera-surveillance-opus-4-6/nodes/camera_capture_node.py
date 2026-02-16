#!/usr/bin/env python3
"""
Camera Capture Node — Throttled Frame Publisher
Subscribes to /camera/image_raw and republishes at a configurable rate (default: 1fps)
for downstream person detection.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import time


class CameraCaptureNode(Node):
    def __init__(self):
        super().__init__('camera_capture_node')

        # Parameters
        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('output_topic', '/surveillance/throttled_image')
        self.declare_parameter('target_fps', 1.0)

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value
        self.target_fps = self.get_parameter('target_fps').get_parameter_value().double_value

        self.min_interval = 1.0 / self.target_fps
        self.last_publish_time = 0.0
        self.frame_count = 0
        self.published_count = 0

        # QoS: best effort for camera (sensor data), reliable for our output
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

        self.publisher = self.create_publisher(
            Image,
            output_topic,
            10
        )

        self.get_logger().info(
            f'Camera Capture Node started: {input_topic} → {output_topic} @ {self.target_fps} fps'
        )

    def image_callback(self, msg: Image):
        self.frame_count += 1
        now = time.time()

        if (now - self.last_publish_time) >= self.min_interval:
            self.publisher.publish(msg)
            self.last_publish_time = now
            self.published_count += 1

            if self.published_count % 10 == 0:
                self.get_logger().info(
                    f'Frames received: {self.frame_count}, published: {self.published_count}'
                )


def main(args=None):
    rclpy.init(args=args)
    node = CameraCaptureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Camera Capture Node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
