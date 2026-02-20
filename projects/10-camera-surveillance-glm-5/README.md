# Camera Surveillance System

A ROS2-style surveillance system for Raspberry Pi with local person detection and email notifications.

## Features

- **Local Processing**: All image processing and detection happens on the Raspberry Pi
- **Person Detection**: Uses MediaPipe for efficient person detection (with Haar cascade fallback)
- **Email Notifications**: Mock email sending with detailed logging
- **1 FPS Detection**: Configurable detection rate to prevent hardware overload
- **Self-Contained**: All logs and captures stored within project folder

## Requirements

- Raspberry Pi with camera module (imx219 or similar)
- Python 3.8+
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)
- PyYAML (`pyyaml`)

## Installation

```bash
# Navigate to project directory
cd ~/.openclaw/openclaw-ros/10-camera-surveillance-glm-5

# Install dependencies
pip3 install -r requirements.txt
```

## Configuration

Edit `config/config.yaml` to customize:

- Camera resolution and FPS
- Detection confidence threshold
- Email recipient address
- Logging settings

## Usage

### Run Surveillance

```bash
# Run with default config
python3 src/surveillance_node.py

# Run with custom config
python3 src/surveillance_node.py -c path/to/config.yaml

# Run with verbose logging
python3 src/surveillance_node.py -v
```

### Test Components

```bash
# Test camera capture
python3 src/camera_capture.py

# Test person detection (provide an image)
python3 src/person_detector.py path/to/image.jpg

# Test notification handler
python3 src/notification_handler.py
```

## Project Structure

```
10-camera-surveillance-glm-5/
├── config/
│   └── config.yaml       # Configuration file
├── src/
│   ├── camera_capture.py     # Camera capture module
│   ├── person_detector.py    # Person detection module
│   ├── notification_handler.py  # Notification module
│   └── surveillance_node.py  # Main orchestrator
├── logs/
│   ├── surveillance.log      # Main log file
│   ├── notifications.log     # Detection notifications
│   └── emails/               # Mock email records
├── captures/                 # Saved detection images
├── requirements.txt
└── README.md
```

## Detection Output

When a person is detected:

1. **Terminal Output**: Real-time alert with detection details
2. **Image Saved**: Annotated image saved to `captures/`
3. **Email Logged**: Mock email content saved to `logs/emails/`
4. **Notification Log**: Entry added to `logs/notifications.log`

### Example Terminal Output

```
================================================================================
🚨 DETECTION ALERT - MOCK EMAIL SENDING
================================================================================
📧 From:    surveillance@localhost
📧 To:      rosie.orchestrate@gmail.com
📅 Time:    2025-02-18T10:30:45.123456
🎯 Confidence: 85.00%
📷 Image:   /path/to/captures/detection_20250218_103045.jpg
--------------------------------------------------------------------------------
✅ Email logged to: logs/emails/email_2025-02-18T10-30-45-123456.txt
================================================================================
```

## Notes

- Detection runs at 1 FPS by default to avoid hardware overload on Raspberry Pi
- A 10-second cooldown prevents notification spam for repeated detections
- Uses MediaPipe pose detection with Haar cascade fallback if MediaPipe is unavailable

## License

MIT License