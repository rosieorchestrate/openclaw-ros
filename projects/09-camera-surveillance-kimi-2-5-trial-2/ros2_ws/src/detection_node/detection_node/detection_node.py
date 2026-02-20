# Copyright 2025 Noah Ploch, Jakub Skupien
# SPDX-License-Identifier: MIT

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
from datetime import datetime


class DetectionNode(Node):
    """
    ROS2 Person Detection Node running at 1Hz.
    Uses MobileNet-SSD for lightweight on-device person detection.
    Publishes detection events and saves capture frames.
    """

    # COCO dataset class ID for person
    PERSON_CLASS_ID = 15

    def __init__(self):
        super().__init__('detection_node')

        # Parameters
        self.declare_parameter('detection_rate_hz', 1.0)
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('capture_dir', '../../captures')
        self.declare_parameter('model_dir', './models')
        self.declare_parameter('input_topic', '/camera/image_raw')  # camera_ros output topic

        self.detection_rate = self.get_parameter('detection_rate_hz').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.capture_dir = os.path.expanduser(
            self.get_parameter('capture_dir').value
        )
        self.model_dir = self.get_parameter('model_dir').value
        self.input_topic = self.get_parameter('input_topic').value

        # Ensure capture directory exists
        os.makedirs(self.capture_dir, exist_ok=True)

        # CV Bridge
        self.bridge = CvBridge()
        self.latest_frame = None
        self.frame_lock = False

        # Load MobileNet-SSD model
        self._load_model()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            self.input_topic,
            self.image_callback,
            10
        )

        # Publishers
        self.detection_pub = self.create_publisher(String, '/detection/events', 10)
        self.debug_pub = self.create_publisher(Image, '/detection/debug', 10)

        # Detection timer (1Hz to avoid hardware overload)
        timer_period = 1.0 / self.detection_rate
        self.timer = self.create_timer(timer_period, self.detection_callback)

        self.get_logger().info(
            f'DetectionNode initialized: {self.detection_rate}Hz, '
            f'confidence > {self.confidence_threshold}, captures → {self.capture_dir}'
        )

    def _load_model(self):
        """Load MobileNet-SSD COCO model for person detection."""
        try:
            # MobileNet-SSD COCO model paths
            prototxt_path = os.path.join(
                self.model_dir,
                'MobileNetSSD_deploy.prototxt'
            )
            model_path = os.path.join(
                self.model_dir,
                'MobileNetSSD_deploy.caffemodel'
            )

            # Check if models exist, download if needed
            if not os.path.exists(prototxt_path) or not os.path.exists(model_path):
                self.get_logger().warning(
                    'MobileNet-SSD model not found. Downloading...'
                )
                self._download_model()

            self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
            self.get_logger().info('MobileNet-SSD model loaded successfully')

        except Exception as e:
            self.get_logger().error(f'Failed to load detection model: {e}')
            # Fallback to HOG detector
            self.get_logger().warning('Falling back to OpenCV HOG detector')
            self.net = None
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def _download_model(self):
        """Download pre-trained MobileNet-SSD model files."""
        import urllib.request

        os.makedirs(self.model_dir, exist_ok=True)

        prototxt_url = 'https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt'
        model_url = 'https://github.com/chuanqi305/MobileNet-SSD/raw/master/mobilenet_iter_73000.caffemodel'

        prototxt_path = os.path.join(self.model_dir, 'MobileNetSSD_deploy.prototxt')
        model_path = os.path.join(self.model_dir, 'MobileNetSSD_deploy.caffemodel')

        try:
            self.get_logger().info(f'Downloading {prototxt_url}...')
            urllib.request.urlretrieve(prototxt_url, prototxt_path)
            self.get_logger().info(f'Downloading {model_url}...')
            urllib.request.urlretrieve(model_url, model_path)
            self.get_logger().info('Model download complete')
        except Exception as e:
            self.get_logger().error(f'Model download failed: {e}')
            raise

    def image_callback(self, msg):
        """Store latest frame for processing."""
        try:
            if not self.frame_lock:
                self.latest_frame = self.bridge.imgmsg_to_cv2(msg, 'rgb8')
        except Exception as e:
            self.get_logger().warning(f'Frame conversion error: {e}')

    def detection_callback(self):
        """Run person detection at 1Hz."""
        if self.latest_frame is None:
            self.get_logger().debug('No frame available for detection')
            return

        # Lock frame during processing
        self.frame_lock = True
        frame = self.latest_frame.copy()
        self.frame_lock = False

        try:
            detections = self._detect_persons(frame)

            if detections:
                self._handle_detection(frame, detections)

        except Exception as e:
            self.get_logger().error(f'Detection error: {e}')

    def _detect_persons(self, frame):
        """Detect persons in frame using MobileNet-SSD or HOG fallback."""
        detections = []

        if self.net is not None:
            # MobileNet-SSD detection
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)),
                0.007843,
                (300, 300),
                127.5
            )
            self.net.setInput(blob)
            outputs = self.net.forward()

            for i in range(outputs.shape[2]):
                confidence = outputs[0, 0, i, 2]
                class_id = int(outputs[0, 0, i, 1])

                if class_id == self.PERSON_CLASS_ID and confidence > self.confidence_threshold:
                    box = outputs[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    detections.append({
                        'bbox': (startX, startY, endX, endY),
                        'confidence': float(confidence)
                    })
        else:
            # HOG fallback detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            (regions, weights) = self.hog.detectMultiScale(
                gray,
                winStride=(4, 4),
                padding=(8, 8),
                scale=1.05
            )
            for i, (x, y, w, h) in enumerate(regions):
                detections.append({
                    'bbox': (x, y, x + w, y + h),
                    'confidence': float(weights[i]) if i < len(weights) else 0.6
                })

        return detections

    def _handle_detection(self, frame, detections):
        """Process detections: log, publish, save capture."""
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')

        # Draw bounding boxes on frame
        debug_frame = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                debug_frame,
                f'Person: {conf:.2f}',
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        # Save capture
        capture_filename = f'detection_{timestamp_str}.jpg'
        capture_path = os.path.join(self.capture_dir, capture_filename)
        cv2.imwrite(capture_path, cv2.cvtColor(debug_frame, cv2.COLOR_RGB2BGR))

        # Publish debug image
        debug_msg = self.bridge.cv2_to_imgmsg(debug_frame, 'rgb8')
        debug_msg.header.stamp = self.get_clock().now().to_msg()
        debug_msg.header.frame_id = 'detection_frame'
        self.debug_pub.publish(debug_msg)

        # Publish detection event
        event_data = {
            'timestamp': timestamp.isoformat(),
            'filename': capture_filename,
            'path': capture_path,
            'person_count': len(detections),
            'confidences': [d['confidence'] for d in detections]
        }
        event_msg = String()
        event_msg.data = str(event_data)
        self.detection_pub.publish(event_msg)

        self.get_logger().info(
            f'DETECTION: {len(detections)} person(s) detected | '
            f'Capture saved: {capture_filename}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Detection node stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()