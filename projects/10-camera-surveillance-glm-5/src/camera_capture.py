#!/usr/bin/env python3
"""
Camera Capture Module
Handles frame capture from Raspberry Pi Camera using libcamera/rpicam
"""

import subprocess
import tempfile
import os
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraCapture:
    """
    Captures frames from Raspberry Pi Camera using rpicam-still.
    Designed for low-frequency capture (1 FPS) to avoid hardware overload.
    """
    
    def __init__(self, width: int = 640, height: int = 480, camera_index: int = 0):
        self.width = width
        self.height = height
        self.camera_index = camera_index
        self._verify_camera()
        
    def _verify_camera(self) -> bool:
        """Verify camera is available."""
        try:
            result = subprocess.run(
                ["rpicam-still", "--list-cameras"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Camera detected:\n{result.stdout}")
                return True
            else:
                logger.error(f"Camera check failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to verify camera: {e}")
            return False
    
    def capture_frame(self) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Capture a single frame from the camera.
        
        Returns:
            Tuple of (frame as numpy array, error message if any)
        """
        try:
            # Use temporary file for capture
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Capture using rpicam-still
            cmd = [
                "rpicam-still",
                "--camera", str(self.camera_index),
                "--width", str(self.width),
                "--height", str(self.height),
                "--output", tmp_path,
                "--nopreview",
                "--immediate"  # Quick capture without preview delay
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                error_msg = f"Capture failed: {result.stderr}"
                logger.error(error_msg)
                return None, error_msg
            
            # Read the captured image
            frame = cv2.imread(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            if frame is None:
                return None, "Failed to read captured image"
            
            logger.debug(f"Captured frame: {frame.shape}")
            return frame, None
            
        except subprocess.TimeoutExpired:
            return None, "Capture timeout"
        except Exception as e:
            logger.error(f"Capture error: {e}")
            return None, str(e)
    
    def capture_to_file(self, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Capture frame directly to a file.
        
        Args:
            output_path: Path to save the captured image
            
        Returns:
            Tuple of (success, error message if any)
        """
        try:
            cmd = [
                "rpicam-still",
                "--camera", str(self.camera_index),
                "--width", str(self.width),
                "--height", str(self.height),
                "--output", output_path,
                "--nopreview",
                "--immediate"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Capture failed: {result.stderr}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)


if __name__ == "__main__":
    # Test the camera capture
    logging.basicConfig(level=logging.INFO)
    
    camera = CameraCapture()
    frame, error = camera.capture_frame()
    
    if frame is not None:
        print(f"✅ Captured frame: {frame.shape}")
        cv2.imwrite("test_capture.jpg", frame)
        print("Saved to test_capture.jpg")
    else:
        print(f"❌ Capture failed: {error}")
