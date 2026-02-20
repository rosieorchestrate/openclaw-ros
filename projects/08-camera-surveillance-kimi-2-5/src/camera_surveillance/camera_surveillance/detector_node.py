#!/usr/bin/env python3
"""
Person Detection Node

Subscribes to camera frames, runs person detection using
MobileNet SSD (lightweight for Raspberry Pi), and publishes
detections at 1 Hz max frequency.

Uses local-only processing - no cloud APIs required.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path


class DetectorNode(Node):
    """ROS2 Node for person detection using MobileNet SSD."""
    
    # COCO dataset class labels MobileNet SSD was trained on
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    
    PERSON_CLASS_ID = 15  # "person" index in CLASSES
    
    def __init__(self):
        super().__init__('detector_node')
        
        # Parameters
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('capture_dir', 'captures')
        self.declare_parameter('model_dir', 'models')
        
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.capture_dir = Path(self.get_parameter('capture_dir').value)
        self.model_dir = Path(self.get_parameter('model_dir').value)
        
        # Ensure directories exist
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.get_logger().info('🔍 Detector Node initializing...')
        self.get_logger().info(f'   Confidence threshold: {self.confidence_threshold}')
        
        # Load detection model
        self.net = self._load_model()
        if self.net is None:
            raise RuntimeError('Failed to load detection model')
        
        # CV Bridge
        self.bridge = CvBridge()
        
        # Track last detection time (rate limiting to 1 Hz)
        self.last_detection_time = 0.0
        self.min_detection_interval = 1.0  # seconds
        
        # ROS2 Subscribers and Publishers
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, qos_profile
        )
        
        self.detection_pub = self.create_publisher(String, 'detection/person', 10)
        self.alert_pub = self.create_publisher(String, 'detection/alert', 10)
        
        # Stats
        self.frames_processed = 0
        self.persons_detected = 0
        self.captures_saved = 0
        
        self.get_logger().info('✅ Detector Node ready - watching for persons')
    
    def _load_model(self):
        """Load MobileNet SSD model (download if needed)."""
        prototxt_path = self.model_dir / 'MobileNetSSD_deploy.prototxt'
        model_path = self.model_dir / 'MobileNetSSD_deploy.caffemodel'
        
        # Download if files don't exist
        if not prototxt_path.exists() or not model_path.exists():
            self.get_logger().info('📥 Downloading MobileNet SSD model...')
            self._download_model()
        
        try:
            net = cv2.dnn.readNetFromCaffe(
                str(prototxt_path),
                str(model_path)
            )
            
            # Use CPU (Raspberry Pi compatible)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            self.get_logger().info('✓ Model loaded successfully')
            return net
            
        except Exception as e:
            self.get_logger().error(f'Failed to load model: {e}')
            return None
    
    def _download_model(self):
        """Download pre-trained MobileNet SSD model files."""
        import urllib.request
        
        prototxt_url = "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt"
        model_url = "https://github.com/chuanqi305/MobileNet-SSD/raw/master/mobilenet_iter_73000.caffemodel"
        
        prototxt_path = self.model_dir / 'MobileNetSSD_deploy.prototxt'
        model_path = self.model_dir / 'MobileNetSSD_deploy.caffemodel'
        
        try:
            self.get_logger().info(f'   Downloading {prototxt_url}...')
            urllib.request.urlretrieve(prototxt_url, prototxt_path)
            
            self.get_logger().info(f'   Downloading model weights...')
            urllib.request.urlretrieve(model_url, model_path)
            
            self.get_logger().info('✓ Model download complete')
        except Exception as e:
            self.get_logger().error(f'Model download failed: {e}')
            raise
    
    def image_callback(self, msg: Image):
        """Process incoming image for person detection."""
        try:
            # Convert ROS Image to OpenCV
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.frames_processed += 1
            
            # Rate limiting - max 1 detection per second
            current_time = self.get_clock().now().seconds_nanoseconds()[0]
            if current_time - self.last_detection_time < self.min_detection_interval:
                return
            
            # Prepare frame for detection
            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)),
                0.007843,
                (300, 300),
                127.5
            )
            
            # Run detection
            self.net.setInput(blob)
            detections = self.net.forward()
            
            # Process detections
            persons_found = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                class_id = int(detections[0, 0, i, 1])
                
                if class_id == self.PERSON_CLASS_ID and confidence > self.confidence_threshold:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    persons_found.append({
                        'confidence': float(confidence),
                        'bbox': [int(startX), int(startY), int(endX), int(endY)]
                    })
            
            if persons_found:
                self._handle_detection(frame, persons_found, msg.header.stamp)
                self.last_detection_time = current_time
            
        except Exception as e:
            self.get_logger().error(f'Detection error: {e}')
    
    def _handle_detection(self, frame, detections, timestamp):
        """Handle person detection - publish alert and save capture."""
        self.persons_detected += 1
        
        # Create detection message
        detection_msg = {
            'timestamp': datetime.now().isoformat(),
            'persons_detected': len(detections),
            'detections': detections
        }
        
        # Publish detection
        msg = String()
        msg.data = json.dumps(detection_msg)
        self.detection_pub.publish(msg)
        
        # Draw bounding boxes on frame
        annotated_frame = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f'Person: {conf:.2f}', 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save capture
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        capture_path = self.capture_dir / f'detection_{timestamp_str}.jpg'
        cv2.imwrite(str(capture_path), annotated_frame)
        self.captures_saved += 1
        
        # Publish alert for email notification
        alert_msg = String()
        alert_msg.data = json.dumps({
            'timestamp': detection_msg['timestamp'],
            'capture_path': str(capture_path),
            'person_count': len(detections),
            'message': f'Person detected! {len(detections)} person(s) found.'
        })
        self.alert_pub.publish(alert_msg)
        
        self.get_logger().warning(f'🚨 PERSON DETECTED! Count: {len(detections)}')
        self.get_logger().info(f'   Capture saved: {capture_path}')
    
    def get_status(self) -> dict:
        """Return current node status."""
        return {
            'frames_processed': self.frames_processed,
            'persons_detected': self.persons_detected,
            'captures_saved': self.captures_saved
        }


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = DetectorNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Detector Node failed: {e}')
    finally:
        if 'node' in locals():
            node.get_logger().info(f'📊 Final stats: {node.get_status()}')
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
