#!/usr/bin/env python3
"""
Person Detector Node — OpenCV DNN MobileNet-SSD
Subscribes to throttled images, runs person detection,
publishes detection events with annotated frames.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import json
import time
import os


class PersonDetectorNode(Node):
    def __init__(self):
        super().__init__('person_detector_node')

        # Parameters
        self.declare_parameter('input_topic', '/surveillance/throttled_image')
        self.declare_parameter('detection_topic', '/surveillance/detection')
        self.declare_parameter('annotated_topic', '/surveillance/annotated_image')
        self.declare_parameter('prototxt_path', '')
        self.declare_parameter('caffemodel_path', '')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('person_class_id', 15)
        self.declare_parameter('input_size', 300)
        self.declare_parameter('project_root', '')

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        detection_topic = self.get_parameter('detection_topic').get_parameter_value().string_value
        annotated_topic = self.get_parameter('annotated_topic').get_parameter_value().string_value
        prototxt = self.get_parameter('prototxt_path').get_parameter_value().string_value
        caffemodel = self.get_parameter('caffemodel_path').get_parameter_value().string_value
        self.confidence_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.person_class_id = self.get_parameter('person_class_id').get_parameter_value().integer_value
        self.input_size = self.get_parameter('input_size').get_parameter_value().integer_value
        self.project_root = self.get_parameter('project_root').get_parameter_value().string_value

        # Ensure captures directory exists
        captures_dir = os.path.join(self.project_root, 'captures', 'detections')
        os.makedirs(captures_dir, exist_ok=True)
        self.captures_dir = captures_dir

        # Load DNN model
        self.get_logger().info(f'Loading MobileNet-SSD from {prototxt}')
        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        self.get_logger().info('MobileNet-SSD loaded successfully')

        self.bridge = CvBridge()
        self.detection_count = 0

        # QoS
        from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            Image,
            input_topic,
            self.image_callback,
            10
        )

        self.detection_pub = self.create_publisher(String, detection_topic, 10)
        self.annotated_pub = self.create_publisher(Image, annotated_topic, 10)

        self.get_logger().info(
            f'Person Detector Node started (threshold={self.confidence_threshold})'
        )

    def image_callback(self, msg: Image):
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'cv_bridge conversion failed: {e}')
            return

        (h, w) = cv_image.shape[:2]
        start_time = time.time()

        # Prepare blob for MobileNet-SSD
        blob = cv2.dnn.blobFromImage(
            cv2.resize(cv_image, (self.input_size, self.input_size)),
            0.007843,
            (self.input_size, self.input_size),
            127.5
        )
        self.net.setInput(blob)
        detections = self.net.forward()

        inference_ms = (time.time() - start_time) * 1000

        # Filter for person detections
        persons = []
        annotated = cv_image.copy()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            class_id = int(detections[0, 0, i, 1])

            if class_id == self.person_class_id and confidence > self.confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype('int')

                # Clamp to image bounds
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                persons.append({
                    'confidence': float(confidence),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })

                # Draw bounding box on annotated image
                label = f'Person {confidence:.2f}'
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(annotated, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if persons:
            self.detection_count += 1
            timestamp = time.strftime('%Y%m%d_%H%M%S')

            # Save annotated frame
            frame_filename = f'detection_{timestamp}_{self.detection_count:04d}.jpg'
            frame_path = os.path.join(self.captures_dir, frame_filename)
            cv2.imwrite(frame_path, annotated)

            # Build detection event
            detection_event = {
                'timestamp': timestamp,
                'detection_id': self.detection_count,
                'num_persons': len(persons),
                'persons': persons,
                'inference_ms': round(inference_ms, 1),
                'frame_path': frame_path,
                'frame_filename': frame_filename,
                'image_size': [w, h]
            }

            # Publish detection
            det_msg = String()
            det_msg.data = json.dumps(detection_event)
            self.detection_pub.publish(det_msg)

            # Publish annotated image
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
            self.annotated_pub.publish(annotated_msg)

            self.get_logger().info(
                f'🚨 PERSON DETECTED #{self.detection_count}: '
                f'{len(persons)} person(s), '
                f'max confidence: {max(p["confidence"] for p in persons):.2f}, '
                f'inference: {inference_ms:.1f}ms, '
                f'saved: {frame_filename}'
            )
        else:
            if self.detection_count == 0:
                # Log periodically when no detections yet
                self.get_logger().debug(
                    f'No person detected (inference: {inference_ms:.1f}ms)'
                )


def main(args=None):
    rclpy.init(args=args)
    node = PersonDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(
            f'Shutting down Person Detector. Total detections: {node.detection_count}'
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
