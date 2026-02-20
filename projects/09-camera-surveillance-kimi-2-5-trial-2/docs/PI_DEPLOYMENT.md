# Raspberry Pi Deployment Guide

## Prerequisites
- Raspberry Pi with camera module connected
- ROS2 Kilted installed
- libcamera installed (`ros-kilted-camera-ros` package)

## Quick Start

### 1. Build Workspace (first time only)
```bash
cd ~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2
./scripts/build_workspace.sh
```

### 2. Run Integration Test
```bash
./scripts/pi_integration_test.sh
```

This will:
- Start camera node
- Start detection node (1Hz person detection)
- Start email node (mock email notifications)
- Run for 30 seconds
- Report results

### 3. Launch Full System
```bash
source ros2_ws/install/setup.bash
ros2 launch surveillance_bringup surveillance.launch.py
```

## Manual Testing

### View Camera Feed
```bash
ros2 run rqt_image_view rqt_image_view
# Select /camera/image_raw topic
```

### Check Frame Rate
```bash
ros2 topic hz /camera/image_raw
```

### Monitor Detections
```bash
ros2 topic echo /detection/events
```

### Trigger Manual Capture
```bash
./scripts/capture_cli.sh capture
```

### View Logs
```bash
# Email notifications
cat logs/mock_emails_*.log

# Detection captures
ls -la captures/
```

## Troubleshooting

### "No cameras available"
- Check camera cable connection
- Verify camera is enabled: `sudo raspi-config` → Interface Options → Camera
- Test with: `libcamera-still --list`

### No detections
- Ensure person is in frame
- Check detection debug output: `ros2 topic hz /detection/debug`
- Verify lighting conditions

### Email not received
- Check email node is running: `ros2 node list | grep email`
- Verify log file created in `logs/`
- Mock mode: Check terminal output for 🚨 alert

## File Locations

| Type | Path |
|------|------|
| Captures | `~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/captures/` |
| Logs | `~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/logs/` |
| Workspace | `~/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2/ros2_ws/` |