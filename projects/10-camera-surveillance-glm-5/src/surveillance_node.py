#!/usr/bin/env python3
"""
Surveillance Node - Main Orchestrator
Coordinates camera capture, person detection, and notifications.
Designed for Raspberry Pi with 1 FPS detection rate.
"""

import sys
import os
import signal
import time
import logging
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from camera_capture import CameraCapture
from person_detector import PersonDetector
from notification_handler import NotificationHandler, DetectionEvent

logger = logging.getLogger(__name__)


class SurveillanceNode:
    """
    Main surveillance orchestrator node.
    
    Responsibilities:
    - Capture frames from camera at configured rate
    - Detect persons using local ML model
    - Send notifications on detection
    - Log all activity
    """
    
    def __init__(self, config_path: str = None):
        self.running = False
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._setup_components()
        self._detection_count = 0
        self._last_detection_time = None
        self._cooldown_seconds = 10  # Minimum time between notifications
        
    def _load_config(self, config_path: str = None) -> dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        else:
            config_path = Path(config_path)
            
        if not config_path.exists():
            logger.warning(f"Config not found at {config_path}, using defaults")
            return self._default_config()
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        logger.info(f"Loaded config from {config_path}")
        return config
    
    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "camera": {
                "device_index": 0,
                "width": 640,
                "height": 480,
                "fps": 1
            },
            "detection": {
                "model": "mediapipe",
                "confidence_threshold": 0.5,
                "save_detections": True
            },
            "notification": {
                "email": {
                    "recipient": "rosie.orchestrate@gmail.com",
                    "sender": "surveillance@localhost"
                },
                "log_dir": "logs",
                "captures_dir": "captures"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/surveillance.log"
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        
        # Create logs directory
        project_root = Path(__file__).parent.parent
        log_dir = project_root / self.config.get("notification", {}).get("log_dir", "logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        log_file = log_dir / "surveillance.log"
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger.info("Logging configured")
        
    def _setup_components(self):
        """Initialize all system components."""
        camera_config = self.config.get("camera", {})
        detection_config = self.config.get("detection", {})
        notification_config = self.config.get("notification", {})
        
        # Initialize camera
        self.camera = CameraCapture(
            width=camera_config.get("width", 640),
            height=camera_config.get("height", 480),
            camera_index=camera_config.get("device_index", 0)
        )
        
        # Initialize detector
        self.detector = PersonDetector(
            confidence_threshold=detection_config.get("confidence_threshold", 0.5)
        )
        self.save_detections = detection_config.get("save_detections", True)
        
        # Initialize notification handler
        email_config = notification_config.get("email", {})
        self.notifier = NotificationHandler(
            recipient_email=email_config.get("recipient", "rosie.orchestrate@gmail.com"),
            sender_email=email_config.get("sender", "surveillance@localhost"),
            log_dir=notification_config.get("log_dir", "logs"),
            captures_dir=notification_config.get("captures_dir", "captures"),
            project_root=str(Path(__file__).parent.parent)
        )
        
        # Detection rate
        self.fps = camera_config.get("fps", 1)
        self.frame_interval = 1.0 / self.fps
        
        logger.info("All components initialized")
        
    def _save_detection_image(self, frame, detections) -> Optional[str]:
        """Save detection image to captures directory."""
        if not self.save_detections:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detection_{timestamp}.jpg"
        filepath = self.notifier.captures_dir / filename
        
        # Draw detections on frame
        annotated_frame = self.detector.draw_detections(frame, detections)
        
        # Save image
        import cv2
        cv2.imwrite(str(filepath), annotated_frame)
        
        logger.info(f"Saved detection image: {filepath}")
        return str(filepath)
        
    def _should_send_notification(self) -> bool:
        """Check if enough time has passed since last notification."""
        if self._last_detection_time is None:
            return True
            
        elapsed = time.time() - self._last_detection_time
        return elapsed >= self._cooldown_seconds
        
    def process_frame(self):
        """Capture and process a single frame."""
        # Capture frame
        frame, error = self.camera.capture_frame()
        
        if error:
            logger.error(f"Capture error: {error}")
            return
            
        if frame is None:
            logger.warning("No frame captured")
            return
            
        # Detect persons
        detections = self.detector.detect(frame)
        
        if detections:
            logger.info(f"🎯 Detected {len(detections)} person(s)")
            
            # Save detection image
            image_path = self._save_detection_image(frame, detections)
            
            # Create detection event
            event = DetectionEvent(
                timestamp=datetime.now().isoformat(),
                confidence=max(d.confidence for d in detections),
                image_path=image_path or "N/A"
            )
            
            # Send notification (with cooldown)
            if self._should_send_notification():
                self.notifier.send_detection_notification(event, image_path)
                self._last_detection_time = time.time()
                self._detection_count += 1
            else:
                logger.debug("Skipping notification (cooldown)")
                
    def run(self):
        """Main surveillance loop."""
        logger.info("=" * 60)
        logger.info("🚀 Starting Surveillance Node")
        logger.info("=" * 60)
        logger.info(f"Camera: {self.camera.width}x{self.camera.height}")
        logger.info(f"Detection rate: {self.fps} FPS")
        logger.info(f"Recipient: {self.notifier.recipient_email}")
        logger.info("=" * 60)
        
        self.running = True
        self._start_time = time.time()
        
        # Main loop
        while self.running:
            loop_start = time.time()
            
            try:
                self.process_frame()
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                
            # Maintain detection rate
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_interval - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        logger.info("Surveillance node stopped")
        
    def stop(self):
        """Stop the surveillance node."""
        logger.info("Stopping surveillance node...")
        self.running = False
        
        # Print summary
        runtime = time.time() - self._start_time if hasattr(self, '_start_time') else 0
        logger.info(f"Summary: {self._detection_count} detections in {runtime:.1f} seconds")
        
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print("\n")  # New line after ^C
        logger.info(f"Received signal {signum}")
        self.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Raspberry Pi Surveillance System")
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose logging",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Create and run node
    node = SurveillanceNode(config_path=args.config)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, node.signal_handler)
    signal.signal(signal.SIGTERM, node.signal_handler)
    
    # Run
    node.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())