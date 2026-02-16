# Status: 06_camera_surveillance

## Latest Test Report (2026-02-16)

### 1. Component Verification
| Component | Status | Method | Results |
|-----------|--------|--------|---------|
| Camera Node | ✅ PASS | `ros2 topic hz` | Stable ~30Hz stream via `camera_ros`. |
| Detector Node | ✅ PASS | Integration Case | Logged successful TFLite XNNPACK initialization. |
| Notifier Node | ✅ PASS | Topic Pub Trigger | Verified log entry in `logs/email_mocks.log`. |

### 2. Physical Verification
- **Test Date**: 2026-02-16 10:39
- **Command**: `ros2 launch surveillance_system surveillance.launch.py`
- **Observations**: 
  - MediaPipe successfully loaded the Pose model.
  - Integration messages correctly propagated from `detector` -> `notifier` via `/detections` topic.
  - Log output confirmed: `DETECTION: [Message]. Sending mock email to rosie.orchestrate@gmail.com`.

### 3. Captured Artifacts
- **Location**: `captures/`
- **Sample File**: `person_20260216_1039XX.jpg` (contains annotated landmarks).

### 4. Known Issues / Notes
- **Hardware**: CPU usage is stable at 1Hz detection interval.
- **Model**: Switched from YOLOv8 to MediaPipe due to ARM instruction set (SIGILL) compatibility issues with standard Torch binaries.
