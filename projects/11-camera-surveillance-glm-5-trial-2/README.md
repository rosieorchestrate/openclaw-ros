# ROS2 Surveillance System

A ROS2-based surveillance system for Raspberry Pi with local person detection and mock email notifications.

## Architecture

```
┌─────────────┐     /camera/image_raw     ┌──────────────────┐     /detection/person     ┌──────────────────┐
│  camera_ros │ ───────────────────────> │  detector_node   │ ───────────────────────> │ notification_node│
│  (libcamera)│     sensor_msgs/Image    │  (MediaPipe)     │     std_msgs/String      │   (mock email)   │
└─────────────┘                          └──────────────────┘                           └──────────────────┘
```

## Nodes

### camera_ros (External)
- Publishes camera images to `/camera/image_raw`
- Uses libcamera for Raspberry Pi camera support

### detector_node
- **Subscribes:** `/camera/image_raw` (sensor_msgs/Image)
- **Publishes:** `/detection/person` (std_msgs/String - JSON)
- Uses MediaPipe for person detection
- Rate-limited to 1 FPS to prevent hardware overload

### notification_node
- **Subscribes:** `/detection/person` (std_msgs/String - JSON)
- Mocks email notifications
- Logs to terminal and files

## Installation

```bash
# Navigate to workspace
cd ~/.openclaw/openclaw-ros/projects/11-camera-surveillance-glm-5-trial-2

# Build the package
source /opt/ros/kilted/setup.bash
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

## Usage

### Quick Start

```bash
# Run with defaults
./run.sh

# Or manually:
source /opt/ros/kilted/setup.bash
source install/setup.bash
ros2 launch surveillance_ros surveillance.launch.py
```

### With Custom Parameters

```bash
ros2 launch surveillance_ros surveillance.launch.py \
    confidence_threshold:=0.7 \
    detection_rate:=2.0 \
    recipient_email:=your@email.com
```

### Run Individual Nodes

```bash
# Run only the detector (requires camera_ros running)
ros2 run surveillance_ros detector_node --ros-args \
    -p confidence_threshold:=0.5 \
    -p detection_rate:=1.0

# Run only the notification handler
ros2 run surveillance_ros notification_node --ros-args \
    -p recipient_email:=rosie.orchestrate@gmail.com
```

## Topics

| Topic | Type | Direction | Description |
|-------|------|-----------|-------------|
| `/camera/image_raw` | sensor_msgs/Image | Published | Camera images from camera_ros |
| `/detection/person` | std_msgs/String | Published | Person detection events (JSON) |

## Parameters

### detector_node
- `confidence_threshold` (double): Detection confidence threshold (default: 0.5)
- `detection_rate` (double): Detection frequency in Hz (default: 1.0)
- `save_detections` (bool): Save detection images (default: true)
- `captures_dir` (string): Directory for saved images (default: ./captures)

### notification_node
- `recipient_email` (string): Email recipient (default: rosie.orchestrate@gmail.com)
- `sender_email` (string): Email sender (default: surveillance@localhost)
- `log_dir` (string): Directory for logs (default: ./logs)
- `cooldown_seconds` (double): Min seconds between notifications (default: 10.0)

## Project Structure

```
11-camera-surveillance-glm-5-trial-2/
├── src/surveillance_ros/
│   ├── surveillance_ros/
│   │   ├── __init__.py
│   │   ├── detector_node.py      # Person detection node
│   │   └── notification_node.py  # Notification handler node
│   ├── launch/
│   │   └── surveillance.launch.py
│   ├── config/
│   │   └── surveillance.yaml
│   ├── package.xml
│   └── setup.py
├── logs/                          # Log files
│   ├── notifications.log
│   └── emails/
├── captures/                      # Detection images
├── run.sh                         # Quick start script
└── README.md
```

## Requirements

- ROS2 Kilted Kaiju
- camera_ros package
- Python packages: opencv-python, mediapipe, numpy

## License

MIT License