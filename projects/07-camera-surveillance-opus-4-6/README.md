# 🎥 ROS2 Camera Surveillance System

A self-contained, Raspberry Pi-based camera surveillance system using ROS2 (Kilted Kaiju) with local person detection via OpenCV DNN (MobileNet-SSD).

## 📋 Overview

- **Camera**: IMX219 (Pi Camera Module v2) via libcamera
- **Detection**: MobileNet-SSD (Caffe) — ~117ms inference on Pi 4B
- **Rate**: 1 frame/second processing to avoid hardware overload
- **Alerts**: Mock email output to terminal + log files (real SMTP ready to add)
- **Snapshots**: Quick CLI-based camera capture

## 🏗️ Architecture

```
/camera/image_raw (30fps from libcamera)
        │
        ▼
[camera_capture_node] ──throttle──▶ /surveillance/throttled_image (1fps)
                                           │
                                           ▼
                                  [person_detector_node]
                                           │
                         ┌─────────────────┼──────────────────┐
                         ▼                 ▼                  ▼
              /surveillance/    /surveillance/      captures/detections/
               detection       annotated_image     (saved frames)
                    │
                    ▼
              [alert_node] → logs/ (mock emails + JSON events)
```

## 📂 Project Structure

```
07-camera-surveillance-opus-4-6/
├── launch/
│   └── surveillance_launch.py    # ROS2 launch file (all nodes)
├── nodes/
│   ├── camera_capture_node.py    # Throttles camera to 1fps
│   ├── person_detector_node.py   # MobileNet-SSD person detection
│   ├── alert_node.py             # Mock email alerts → logs
│   └── snapshot_node.py          # Single-frame CLI capture
├── models/
│   ├── deploy.prototxt           # MobileNet-SSD architecture
│   └── mobilenet_ssd.caffemodel  # Pre-trained weights (~23MB)
├── config/
│   └── surveillance_config.yaml  # System configuration
├── scripts/
│   ├── start.sh                  # Launch full surveillance system
│   ├── stop.sh                   # Stop all surveillance nodes
│   ├── snapshot.sh               # Quick camera snapshot
│   └── test_detection.sh         # Test detection pipeline offline
├── logs/                         # Alert logs (auto-created)
├── captures/
│   ├── detections/               # Saved detection frames
│   └── snapshots/                # Manual camera snapshots
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

```bash
# ROS2 Kilted Kaiju must be installed
source /opt/ros/kilted/setup.bash

# Required ROS2 packages (should already be installed):
# ros-kilted-camera-ros, ros-kilted-cv-bridge, ros-kilted-sensor-msgs
```

### 1. Test Detection Pipeline (No Camera Needed)

```bash
cd 07-camera-surveillance-opus-4-6
./scripts/test_detection.sh

# With a specific test image:
./scripts/test_detection.sh /path/to/test_image.jpg
```

### 2. Take a Quick Snapshot

```bash
./scripts/snapshot.sh                  # Timestamped filename
./scripts/snapshot.sh check_angle      # Custom: check_angle.jpg
```

### 3. Start Full Surveillance

```bash
./scripts/start.sh
```

This launches all 4 nodes. You'll see:
- Camera initialization
- Throttled frame publishing (1fps)
- Detection results (with 🚨 alerts when persons detected)
- Mock email output in terminal + saved to `logs/`

### 4. Stop Surveillance

```bash
./scripts/stop.sh
# or Ctrl+C in the start.sh terminal
```

## 📊 Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/camera/image_raw` | `sensor_msgs/Image` | Raw camera feed (30fps) |
| `/surveillance/throttled_image` | `sensor_msgs/Image` | Throttled to 1fps |
| `/surveillance/detection` | `std_msgs/String` | Detection events (JSON) |
| `/surveillance/annotated_image` | `sensor_msgs/Image` | Annotated frames |

## ⚙️ Configuration

Edit `config/surveillance_config.yaml` to adjust:
- `detection_fps`: Processing rate (default: 1.0)
- `confidence_threshold`: Detection sensitivity (default: 0.5)
- `alert_cooldown_seconds`: Minimum time between alerts (default: 30)
- `mock_mode`: Toggle mock/real email sending

## 📧 Alert System

### Mock Mode (Default)
- Prints formatted email content to terminal
- Saves to `logs/alerts_YYYY-MM-DD.log`
- JSON events logged to `logs/detection_events_YYYY-MM-DD.jsonl`
- Detection frames saved to `captures/detections/`

### Real Email (Future)
Set `mock_mode: false` in config and configure SMTP credentials.

## 🔧 Manual Node Launch

You can also run individual nodes for testing:

```bash
source /opt/ros/kilted/setup.bash
PROJECT_ROOT=$(pwd)

# Camera only
ros2 run camera_ros camera_node --ros-args -p width:=640 -p height:=480

# Capture node
python3 nodes/camera_capture_node.py --ros-args -p target_fps:=1.0

# Detector
python3 nodes/person_detector_node.py --ros-args \
  -p prototxt_path:=$PROJECT_ROOT/models/deploy.prototxt \
  -p caffemodel_path:=$PROJECT_ROOT/models/mobilenet_ssd.caffemodel \
  -p project_root:=$PROJECT_ROOT

# Alert
python3 nodes/alert_node.py --ros-args \
  -p project_root:=$PROJECT_ROOT \
  -p mock_mode:=true
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Pi Model | Raspberry Pi 4B, 3.7GB RAM |
| Inference Time | ~117ms per frame |
| Max FPS (detection) | ~8.5 FPS |
| Operating FPS | 1 FPS (configurable) |
| Model Size | 23MB (MobileNet-SSD Caffe) |
| CPU Load @ 1fps | ~12% single core |

## 🔮 Roadmap

- [ ] Real SMTP email sending
- [ ] Web dashboard for live view
- [ ] Detection zone masking
- [ ] Multi-camera support
- [ ] Recording mode (continuous + event-triggered)
