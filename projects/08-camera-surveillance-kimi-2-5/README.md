# 08-camera-surveillance-kimi-2-5

ROS2-based local camera surveillance system with person detection and email alerts.
Designed for Raspberry Pi with libcamera-compatible cameras.

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Camera    │────▶│   Detector  │────▶│    Email    │
│    Node     │     │    Node     │     │    Node     │
│  (1 Hz)     │     │(MobileNet   │     │  (Mock/     │
│             │     │    SSD)     │     │   Real)     │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Captures   │
                    │  Logs       │
                    └─────────────┘
```

**Key Features:**
- ⚡ **Local processing** — Person detection runs entirely on-device (MobileNet SSD)
- 🎯 **1 Hz detection rate** — Prevents hardware overload on Raspberry Pi
- 📧 **Mock email mode** — Logs alerts to terminal and file for testing
- 🧪 **Testable** — Quick camera capture script included
- 📦 **Self-contained** — All logs and captures within project folder

---

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi (tested on Pi 4)
- ROS2 Kilted (or compatible)
- libcamera-compatible camera (imx219 verified)
- Python packages: `opencv-python`, `numpy`

### 1. Initial Setup
```bash
cd ~/.openclaw/openclaw-ros/projects/08-camera-surveillance-kimi-2-5
./scripts/spinup.sh
```

This script:
- ✅ Verifies camera connection
- ✅ Builds the ROS2 workspace
- ✅ Creates necessary directories
- ✅ Checks Python dependencies

### 2. Test Camera
```bash
./scripts/grab_frame.sh
```
Captures a single frame to `captures/test_<timestamp>.jpg`

### 3. Launch Surveillance
```bash
# Source the workspace
source install/local_setup.bash

# Launch in mock mode (recommended for testing)
ros2 launch camera_surveillance surveillance.launch.py

# Or with custom parameters
ros2 launch camera_surveillance surveillance.launch.py \
    mock_mode:=true \
    confidence_threshold:=0.6 \
    email_to:=your@email.com
```

### 4. Monitor Output
```bash
# Watch mock email log
tail -f logs/mock_emails.log

# View detection captures
ls -la captures/
```

---

## 📁 Project Structure

```
08-camera-surveillance-kimi-2-5/
├── src/camera_surveillance/          # ROS2 package
│   ├── camera_surveillance/          # Python modules
│   │   ├── camera_node.py            # Camera capture node
│   │   ├── detector_node.py          # Person detection node
│   │   └── email_node.py             # Email notification node
│   ├── launch/
│   │   └── surveillance.launch.py    # Launch configuration
│   ├── config/
│   │   └── surveillance.yaml         # Node parameters
│   ├── setup.py
│   └── package.xml
├── scripts/
│   ├── spinup.sh                     # One-command setup
│   └── grab_frame.sh                 # Quick camera test
├── logs/                             # Application logs (created on run)
├── captures/                         # Detection images (created on run)
├── models/                           # ML models (auto-downloaded)
└── README.md
```

---

## ⚙️ Configuration

Edit `src/camera_surveillance/config/surveillance.yaml` or use launch arguments:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `capture_rate_hz` | 1.0 | Camera capture frequency (Hz) |
| `confidence_threshold` | 0.5 | Person detection confidence (0.0-1.0) |
| `mock_mode` | true | Log to file (true) or send real email (false) |
| `email_to` | rosie.orchestrate@gmail.com | Alert recipient |

---

## 🧪 Testing

### Without Camera (Unit Tests)
```bash
# Run colcon tests
cd ~/.openclaw/openclaw-ros/08-camera-surveillance-kimi-2-5
colcon test --packages-select camera_surveillance
```

### Manual Testing
```bash
# 1. Check camera is detected
cam --list

# 2. Grab test frame
./scripts/grab_frame.sh

# 3. Launch in mock mode
source install/local_setup.bash
ros2 launch camera_surveillance surveillance.launch.py

# 4. Trigger detection (stand in front of camera)
# 5. Check logs
ls -la captures/  # Should see detection_*.jpg
tail logs/mock_emails.log
```

---

## 🔧 Troubleshooting

### Camera Not Detected
```bash
# Verify libcamera
sudo apt install libcamera-tools
cam --list  # Should show imx219

# Check camera connection
sudo raspi-config  # Enable camera interface
```

### Build Errors
```bash
# Clean and rebuild
cd ~/.openclaw/openclaw-ros/projects/08-camera-surveillance-kimi-2-5
rm -rf build/ install/ log/
colcon build --packages-select camera_surveillance --symlink-install
```

### High CPU Temperature
The system caps detection at 1 Hz to protect the Pi. If temp exceeds 75°C:
- Add heatsinks/fan
- Reduce capture resolution in launch file
- Increase detection interval

---

## 📝 Logging

**Mock Mode Output:**
```
[email_node-3] 🚨 PERSON DETECTED!
[email_node-3]    Confidence: 87.3%
[email_node-3]    Time: 14:32:15
[email_node-3]    [MOCK EMAIL - See logs for details]
```

**Log Files:**
- `logs/mock_emails.log` — Full email content (mock mode)
- `captures/detection_*.jpg` — Detection frames with bounding boxes

---

## 🛡️ Safety & Limits

Per **Rosie Robotics** principles:
- **Velocity Limits:** 1 Hz max capture rate to prevent overload
- **Logging:** All operations logged for debugging
- **Mock First:** Email defaults to mock mode (safe testing)
- **E-Stop:** Press `Ctrl+C` to stop all nodes gracefully

---

## 🔮 Future Enhancements

- Real email mode (configure SMTP)
- Multiple camera support
- Web dashboard
- Motion detection (pre-filter before ML)
- MQTT integration

---

**Built with ❤️ by Rosie (ROS2 Orchestrator)**  
*Reflective Discovery | Engineering Rigor | Proactive Communication*
