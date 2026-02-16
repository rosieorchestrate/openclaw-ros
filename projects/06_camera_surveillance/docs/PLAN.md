# Plan: 06_camera_surveillance

## Objective
Develop a ROS2-based surveillance system on Raspberry Pi using local YOLO detection.
- Local image processing.
- Person detection triggers a (mock) email with the captured frame.
- Detection rate: 1Hz (to save CPU/Thermal headroom).
- Modular architecture with clear verification steps.

## Components
1. **Camera Node**: Captures frames from the RPi camera (using `v4l2_camera` or a custom wrapper).
2. **Detection Node**: Runs YOLO (likely YOLOv8n or TFLite version) at 1Hz on incoming frames.
3. **Notification Node**: Mocks email sending, logs detection details, and prepares for future SMTP integration.

## Constraints
- **Hardware**: Raspberry Pi (local inference).
- **Frequency**: 1Hz detection limit.
- **Output**: Terminal logs + Frame capture in a local directory.

## Step-by-Step Execution
1. [ ] Project Initialization (Workspaces & Folders)
2. [ ] Documentation: SIMULATION_CONTRACT.md & VERIFICATION_CONTRACT.md
3. [ ] Mock Email/Notification Node Implementation
4. [ ] Camera Node Setup & Frame Handling
5. [ ] YOLO Local Inference Integration (Optimization for RPi)
6. [ ] Integration & Stress Test (Monitoring CPU Temp)
