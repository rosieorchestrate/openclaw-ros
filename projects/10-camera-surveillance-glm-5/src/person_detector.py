#!/usr/bin/env python3
"""
Person Detection Module
Uses MediaPipe for lightweight person detection on Raspberry Pi
"""

import logging
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents a detected person."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    label: str = "person"
    
    @property
    def area(self) -> int:
        """Calculate bounding box area."""
        return self.bbox[2] * self.bbox[3]
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get center point of bounding box."""
        x, y, w, h = self.bbox
        return (x + w // 2, y + h // 2)


class PersonDetector:
    """
    Person detection using MediaPipe Object Detection.
    Optimized for Raspberry Pi with 1 FPS detection rate.
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self._model_loaded = False
        self._detector = None
        self._load_model()
        
    def _load_model(self):
        """Load MediaPipe object detection model."""
        try:
            import mediapipe as mp
            
            # Use MediaPipe's object detection
            self.mp_tasks = mp.tasks
            self.mp_vision = mp.tasks.vision
            
            # Create object detector options
            base_options = self.mp_tasks.BaseOptions(
                model_asset_path='efficientdet.tflite'
            )
            
            # For person detection, we'll use the pose detection which is more reliable
            # for people and available by default
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            
            self._model_loaded = True
            logger.info("MediaPipe pose detection model loaded")
            
        except Exception as e:
            logger.warning(f"Could not load MediaPipe: {e}")
            logger.info("Falling back to Haar cascade detection")
            self._model_loaded = False
            self._load_haar_fallback()
    
    def _load_haar_fallback(self):
        """Load Haar cascade as fallback for person detection."""
        try:
            self._haar_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            )
            self._face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            logger.info("Haar cascade detectors loaded as fallback")
            self._use_haar = True
        except Exception as e:
            logger.error(f"Failed to load Haar cascades: {e}")
            self._use_haar = False
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect persons in a frame.
        
        Args:
            frame: BGR image as numpy array
            
        Returns:
            List of Detection objects
        """
        if frame is None:
            return []
        
        detections = []
        
        try:
            if hasattr(self, '_use_haar') and self._use_haar:
                detections = self._detect_haar(frame)
            else:
                detections = self._detect_mediapipe(frame)
                
        except Exception as e:
            logger.error(f"Detection error: {e}")
            
        return detections
    
    def _detect_mediapipe(self, frame: np.ndarray) -> List[Detection]:
        """Detect persons using MediaPipe pose detection."""
        detections = []
        
        with self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=0,  # Lightest model for Pi
            min_detection_confidence=self.confidence_threshold,
            min_tracking_confidence=0.5
        ) as pose:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Get bounding box from landmarks
                h, w = frame.shape[:2]
                landmarks = results.pose_landmarks.landmark
                
                # Find bounding box from all landmarks
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
                    
                    bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
                    
                    # Calculate average confidence from visible landmarks
                    visible_landmarks = [lm.visibility for lm in landmarks if lm.visibility > 0.5]
                    confidence = sum(visible_landmarks) / len(visible_landmarks) if visible_landmarks else 0.5
                    
                    detections.append(Detection(
                        bbox=bbox,
                        confidence=confidence,
                        label="person"
                    ))
                    
                    logger.info(f"Person detected with confidence: {confidence:.2f}")
        
        return detections
    
    def _detect_haar(self, frame: np.ndarray) -> List[Detection]:
        """Detect persons using Haar cascades (fallback)."""
        detections = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Try full body detection
        bodies = self._haar_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(50, 100)
        )
        
        for (x, y, w, h) in bodies:
            detections.append(Detection(
                bbox=(int(x), int(y), int(w), int(h)),
                confidence=0.6,  # Haar doesn't provide confidence
                label="person_body"
            ))
        
        # Also try face detection for better accuracy
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(30, 30)
        )
        
        for (x, y, w, h) in faces:
            # Check if this face is already inside a body detection
            face_center = (x + w//2, y + h//2)
            already_detected = any(
                bx <= face_center[0] <= bx + bw and 
                by <= face_center[1] <= by + bh
                for (bx, by, bw, bh) in bodies
            )
            
            if not already_detected:
                detections.append(Detection(
                    bbox=(int(x), int(y), int(w), int(h)),
                    confidence=0.7,
                    label="person_face"
                ))
        
        if detections:
            logger.info(f"Detected {len(detections)} person(s) using Haar cascades")
            
        return detections
    
    def draw_detections(
        self, 
        frame: np.ndarray, 
        detections: List[Detection]
    ) -> np.ndarray:
        """
        Draw detection bounding boxes on frame.
        
        Args:
            frame: BGR image
            detections: List of Detection objects
            
        Returns:
            Frame with drawn detections
        """
        result = frame.copy()
        
        for det in detections:
            x, y, w, h = det.bbox
            
            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{det.label}: {det.confidence:.2f}"
            cv2.putText(
                result, 
                label, 
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        return result


if __name__ == "__main__":
    # Test the detector
    logging.basicConfig(level=logging.INFO)
    
    # Create a test frame
    detector = PersonDetector(confidence_threshold=0.5)
    
    # Test with a sample image if available
    import sys
    if len(sys.argv) > 1:
        frame = cv2.imread(sys.argv[1])
        if frame is not None:
            detections = detector.detect(frame)
            print(f"✅ Detected {len(detections)} person(s)")
            for d in detections:
                print(f"   - {d.label}: confidence={d.confidence:.2f}, bbox={d.bbox}")
            
            # Draw and save
            result = detector.draw_detections(frame, detections)
            cv2.imwrite("test_detection.jpg", result)
            print("Saved to test_detection.jpg")
    else:
        print("Usage: python person_detector.py <image_path>")