#!/usr/bin/env python3
"""
Quick Frame Capture Utility
Captures a single frame and saves it for inspection.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from camera_capture import CameraCapture
import cv2


def capture_frame(output_path: str = None):
    """Capture a frame and save to file."""
    camera = CameraCapture(width=640, height=480)
    
    print("📷 Capturing frame...")
    frame, error = camera.capture_frame()
    
    if error:
        print(f"❌ Error: {error}")
        return None
    
    if frame is None:
        print("❌ No frame captured")
        return None
    
    # Generate output path if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = Path(__file__).parent
        output_path = project_root / "captures" / f"frame_{timestamp}.jpg"
    else:
        output_path = Path(output_path)
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save frame
    cv2.imwrite(str(output_path), frame)
    print(f"✅ Frame saved: {output_path}")
    print(f"   Dimensions: {frame.shape[1]}x{frame.shape[0]}")
    
    return str(output_path)


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else None
    result = capture_frame(output)
    if result:
        print(f"\n📸 Image ready: {result}")
