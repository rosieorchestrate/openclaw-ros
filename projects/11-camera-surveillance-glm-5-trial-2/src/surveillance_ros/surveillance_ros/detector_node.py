#!/usr/bin/env python3
"""
Person Detector Node for ROS2
Subscribes to camera images and detects persons using MediaPipe.
Publishes detection events to /detection/person topic.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PersonDetectorNode(Node):
    """
    ROS2 node that detects persons in camera images.
    
    Subscribes to:
        /camera/image_raw (sensor_msgs/Image): Camera images from camera_ros
        
    Publishes:
        /detection/person (std_msgs/String): JSON detection events
        
    Parameters:
        confidence_threshold: Minimum confidence for detection (default: 0.5)
        detection_rate: Detection frequency in Hz (default: 1.0)
        save_detections: Save detection images (default: True)
        captures_dir: Directory for saved images (default: ./captures)
    """
    
    def __init__(self):
        super().__init__('person_detector')
        
        # Declare parameters
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('detection_rate', 1.0)
        self.declare_parameter('save_detections', True)
        self.declare_parameter('captures_dir', './captures')
        self.declare_parameter('image_topic', '/camera/image_raw')
        
        # Get parameters
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.detection_rate = self.get_parameter('detection_rate').value
        self.save_detections = self.get_parameter('save_detections').value
        self.captures_dir = Path(self.get_parameter('captures_dir').value)
        self.image_topic = self.get_parameter('image_topic').value
        
        # Ensure captures directory exists
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        
        # CV Bridge for converting ROS images
        self.bridge = CvBridge()
        
        # QoS profile for camera (usually best effort)
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            depth=1
        )
        
        # Subscriber for camera images
        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            qos
        )
        
        # Publisher for detection events
        self.detection_publisher = self.create_publisher(
            String,
            '/detection/person',
            10
        )
        
        # Detection timing
        self.last_detection_time = 0.0
        self.detection_interval = 1.0 / self.detection_rate
        
        # Load detection model
        self._load_detector()
        
        # Detection counter
        self.detection_count = 0
        
        self.get_logger().info(f'Person Detector Node initialized')
        self.get_logger().info(f'  Image topic: {self.image_topic}')
        self.get_logger().info(f'  Detection rate: {self.detection_rate} Hz')
        self.get_logger().info(f'  Confidence threshold: {self.confidence_threshold}')
        self.get_logger().info(f'  Captures directory: {self.captures_dir}')
        
    def _load_detector(self):
        """Load MediaPipe pose detection model."""
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=0,  # Lightest model for Pi
                min_detection_confidence=self.confidence_threshold,
                min_tracking_confidence=0.5
            )
            self.use_mediapipe = True
            self.get_logger().info('MediaPipe pose detection model loaded')
        except Exception as e:
            self.get_logger().warn(f'Could not load MediaPipe: {e}')
            self.get_logger().info('Falling back to Haar cascade detection')
            self._load_haar_fallback()
            
    def _load_haar_fallback(self):
        """Load Haar cascade as fallback."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.body_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_fullbody.xml'
        )
        self.use_mediapipe = False
        self.get_logger().info('Haar cascade detectors loaded')
        
    def image_callback(self, msg: Image):
        """Process incoming camera images."""
        current_time = self.get_clock().now().nanoseconds / 1e9
        
        # Rate limiting
        if current_time - self.last_detection_time < self.detection_interval:
            return
            
        self.last_detection_time = current_time
        
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Detect persons
            detections = self.detect_persons(cv_image)
            
            if detections:
                self.get_logger().info(f'Detected {len(detections)} person(s)')
                
                # Save detection image if enabled
                image_path = None
                if self.save_detections:
                    image_path = self.save_detection_image(cv_image, detections)
                    
                # Publish detection event
                self.publish_detection(detections, image_path, msg.header.stamp)
                
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')
            
    def detect_persons(self, image: np.ndarray) -> list:
        """
        Detect persons in an image.
        
        Args:
            image: BGR image as numpy array
            
        Returns:
            List of detection dictionaries with bbox and confidence
        """
        detections = []
        
        if self.use_mediapipe:
            detections = self._detect_mediapipe(image)
        else:
            detections = self._detect_haar(image)
            
        return detections
        
    def _detect_mediapipe(self, image: np.ndarray) -> list:
        """Detect persons using MediaPipe pose."""
        detections = []
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks:
            h, w = image.shape[:2]
            landmarks = results.pose_landmarks.landmark
            
            # Get bounding box from visible landmarks
            x_coords = [lm.x * w for lm in landmarks if lm.visibility > 0.5]
            y_coords = [lm.y * h for lm in landmarks if lm.visibility > 0.5]
            
            if x_coords and y_coords:
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))
                
                # Add padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                # Calculate confidence
                visible_landmarks = [lm.visibility for lm in landmarks if lm.visibility > 0.5]
                confidence = sum(visible_landmarks) / len(visible_landmarks)
                
                detections.append({
                    'bbox': [x_min, y_min, x_max - x_min, y_max - y_min],
                    'confidence': float(confidence),
                    'label': 'person'
                })
                
        return detections
        
    def _detect_haar(self, image: np.ndarray) -> list:
        """Detect persons using Haar cascades."""
        detections = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Face detection
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
        )
        
        for (x, y, w, h) in faces:
            detections.append({
                'bbox': [int(x), int(y), int(w), int(h)],
                'confidence': 0.7,
                'label': 'person_face'
            })
            
        return detections
        
    def save_detection_image(self, image: np.ndarray, detections: list) -> str:
        """Save image with detection bounding boxes."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f'detection_{timestamp}.jpg'
        filepath = self.captures_dir / filename
        
        # Draw detections
        annotated = image.copy()
        for det in detections:
            x, y, w, h = det['bbox']
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{det['label']}: {det['confidence']:.2f}"
            cv2.putText(annotated, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        cv2.imwrite(str(filepath), annotated)
        self.get_logger().debug(f'Saved detection image: {filepath}')
        
        return str(filepath)
        
    def publish_detection(self, detections: list, image_path: str = None, stamp=None):
        """Publish detection event."""
        self.detection_count += 1
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'count': self.detection_count,
            'detections': detections,
            'image_path': image_path,
            'max_confidence': max(d['confidence'] for d in detections)
        }
        
        msg = String()
        msg.data = json.dumps(event)
        self.detection_publisher.publish(msg)
        
        self.get_logger().info(f'Published detection event #{self.detection_count}')


def main(args=None):
    rclpy.init(args=args)
    
    node = PersonDetectorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info(f'Shutting down. Total detections: {node.detection_count}')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()