# 09 Camera Surveillance - ROS2 Person Detection System

## Overview
ROS2-based camera surveillance system running on Raspberry Pi with local person detection. Upon detecting a person, the system sends email notifications with captured frames.

## Project Structure
```
.
├── ros2_ws/                    # ROS2 workspace
│   └── src/
│       ├── camera_node/        # libcamera → ROS2 image publisher
│       ├── detection_node/     # 1Hz person detection
│       └── email_node/         # Mock email service + logging
├── logs/                       # Application logs
├── captures/                   # Detection frame captures
├── scripts/                    # Setup/utility scripts
└── docs/                       # Documentation

## Key Requirements
- **Platform**: Raspberry Pi with libcamera-compatible camera
- **Detection Frequency**: 1 Hz (once per second)
- **Processing**: Local on-device (no cloud)
- **Notification**: Email with attached detection frame
- **Email Mode**: Mock (logs to terminal + file)

## Quick Start

### 1. Build the Workspace
```bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 2. Launch the System
```bash
ros2 launch surveillance_system bringup.launch.py
```

## Development Status
- [x] Project structure created
- [x] Phase 1: Camera Node (camera_ros via apt)
- [x] Phase 2: Detection Node (1Hz MobileNet-SSD person detection)
- [x] Phase 3: Email Node (mock email + logging)
- [x] Launch file integration
- [x] On-demand capture service
- [ ] Build and test on Raspberry Pi

## Architecture

```
                    ┌─────────────────┐
                    │  capture_service │◀── CLI: capture_cli.sh
                    │  (on-demand)    │    Services: /capture_*
                    └────────┬────────┘
                             │
                             ▼
                    captures/capture_*.jpg
                             │
┌─────────────┐              │        ┌─────────────┐
│ camera_ros  │──────────────┴───────▶│   email     │
│ (libcamera) │     /camera/image_raw │   node      │
└─────────────┘              │        └──────┬──────┘
                             │               │
                             ▼               ▼
┌─────────────┐     captures/        logs/mock_emails_*.log
│  detection  │────▶detection_*.jpg   terminal output
│  node (1Hz) │         ↑            (mock email with
└──────┬──────┘    (with bounding    detection data)
       │              boxes)
       │
       ▼
/detection/events (JSON: timestamp, filename, path, count, confidences)
```

### Data Flow

| Stage | Input | Processing | Output |
|-------|-------|------------|--------|
| **Camera** | Pi Camera Module | libcamera → ROS2 | `/camera/image_raw` (10Hz) |
| **Detection** | `/camera/image_raw` | MobileNet-SSD @ 1Hz | `captures/detection_*.jpg` (annotated) |
| | | Draws bounding boxes | `/detection/events` (JSON) |
| **Email** | `/detection/events` | Format mock email | Terminal output + `logs/mock_emails_*.log` |
| | | | References frame path for "attachment" |
| **Capture** | `/camera/image_raw` | On-demand or 1Hz | `captures/capture_*.jpg` |

## Quick Start

### 1. Build the Workspace
```bash
cd ~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2
./scripts/build_workspace.sh
```

### 2. Launch the System
```bash
source ros2_ws/install/setup.bash
ros2 launch surveillance_bringup surveillance.launch.py
```

### 3. Verify Topics
```bash
# List all topics
ros2 topic list

# Check camera stream
ros2 topic hz /camera/image_raw

# Monitor detections
ros2 topic echo /detection/events
```

## Configuration

Launch arguments:
- `camera_width`: Camera resolution width (default: 640)
- `camera_height`: Camera resolution height (default: 480)
- `detection_rate`: Detection frequency in Hz (default: 1.0)
- `target_email`: Email for notifications (default: rosie.orchestrate@gmail.com)

## On-Demand Capture (New!)

Capture frames while the application is running via ROS2 services:

```bash
# Single frame capture
./scripts/capture_cli.sh capture

# Start continuous capture (1Hz)
./scripts/capture_cli.sh start

# Stop continuous capture
./scripts/capture_cli.sh stop

# Check service status
./scripts/capture_cli.sh status
```

Or use ROS2 service calls directly:
```bash
ros2 service call /capture_frame std_srvs/srv/Trigger {}
ros2 service call /capture_start_continuous std_srvs/srv/Trigger {}
ros2 service call /capture_stop_continuous std_srvs/srv/Trigger {}
```

Services:
| Service | Description |
|---------|-------------|
| `/capture_frame` | Capture single frame immediately |
| `/capture_start_continuous` | Start 1Hz continuous capture |
| `/capture_stop_continuous` | Stop continuous capture |

## Testing the Flow

### Option 1: Full System Test (requires Pi + camera)
```bash
# Terminal 1: Launch everything
ros2 launch surveillance_bringup surveillance.launch.py

# Terminal 2: Verify camera stream
ros2 topic hz /camera/image_raw

# Terminal 3: Monitor detections
ros2 topic echo /detection/events

# Terminal 4: Trigger manual capture
./scripts/capture_cli.sh capture
```

### Option 2: Email Flow Test (no camera needed)
```bash
# Start just the email node
ros2 run email_node email_node

# In another terminal, simulate a detection:
./scripts/test_email_flow.sh
```

### Option 3: Verify Complete Flow Diagram
```bash
./scripts/verify_complete_flow.sh
```

### Expected Email Output
When a person is detected, the email node outputs:

```
🚨 PERSON DETECTED - MOCK EMAIL SENT

================================================================================
                    📧  MOCK EMAIL NOTIFICATION  📧
================================================================================

To: rosie.orchestrate@gmail.com
From: surveillance-system@ros2.local
Subject: [ALERT] Person Detected - 2025-02-17T18:15:30.123456

--- DETECTION DATA ---
Persons detected: 1
Confidence scores: 0.85
Capture filename: detection_20250217_181530.jpg
Capture path: /home/user/.../captures/detection_20250217_181530.jpg

--- ATTACHMENT ---
[This email would include the detection frame as an attachment]
Filename: detection_20250217_181530.jpg
Full path: /home/user/.../captures/detection_20250217_181530.jpg

--- BOUNDING BOX INFO ---
Frame includes: Green bounding boxes drawn around detected persons
                 Confidence score labels above each box

[MOCK MODE - No email actually sent. Logged to file only.]

================================================================================
```

## Authors
- Noah Ploch
- Jakub Skupien
