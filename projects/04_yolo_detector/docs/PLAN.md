# Plan: YOLO Detector (Milestone 1)
Last Updated: 2026-02-14

## Objective
Create a ROS 2 application that performs local object detection using YOLO. It must process one frame per second and log detected objects (label, confidence) to unique, persistent log files.

## Roadmap
- [ ] **Step 1: Environment & Dependency Audit**: 
  - Verify `ultralytics` or `opencv-python` (DNN) availability on Pi 4.
  - Choose model (YOLOv8n or YOLOv11n for CPU efficiency).
- [ ] **Step 2: Simulation Level 2 (Real Processing)**:
  - Implement a `yolo_detector` node.
  - Use `virtual_camera` (from Project 03) to stream test patterns/images.
- [ ] **Step 3: Logic Verification**:
  - Verify unique log file creation per run.
  - Verify structured logging of detections.
- [ ] **Step 4: Hardware Integration**:
  - Connect to physical `camera_ros`.
  - Perform real-world benchmarking (CPU usage check - 80% rule).

## Simulation Strategy
- **Level**: 2 (Real Processing).
- **Inference**: Local CPU-based inference.
- **Trigger**: None (Continuous 1Hz sampling).
