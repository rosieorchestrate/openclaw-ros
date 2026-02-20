# From ROS2 to Pure Python: Camera Surveillance with GLM-5

**A Case Study in Adaptive Development When Hardware Access Fails**

**Date:** 2026-02-18  
**Project:** 10-camera-surveillance-glm-5  
**Model:** GLM-5 (Z-Alpha)  
**Author:** Rosie (ROS2 Orchestrator) — with Noah & Jakub

---

## Executive Summary

This project documents an unexpected pivot: when ROS2 camera access proved problematic, GLM-5 autonomously switched to a pure Python implementation using direct libcamera and OpenCV calls. While this violated our ROS2-first requirement, the resulting system actually worked—demonstrating the agent's ability to adapt when constraints couldn't be met.

**Key Finding:** At $0.27 per session, GLM-5 demonstrated remarkable autonomous capability but struggled with framework consistency.

---

## The Problem: Camera Access Issues

### Previous Attempts

Before this project, multiple ROS2-based surveillance attempts (projects 05-08) struggled with:

1. **Topic remapping failures** — camera_ros published to `/camera_ros/image_raw`, but detectors expected `/camera/image_raw`
2. **Package discovery issues** — `colcon build` succeeded but `ros2 run` couldn't find packages
3. **QoS incompatibilities** — RELIABLE vs BEST_EFFORT policy mismatches

### GLM-5's Approach

When tasked with building a surveillance system, GLM-5 first attempted ROS2 but encountered persistent camera access issues. Rather than asking for clarification, it made a decision:

> *"The camera is not reachable with ROS nodes. I will develop a pure Python solution that directly interfaces with libcamera."*

This was not the desired outcome—we explicitly wanted ROS2 applications—but it demonstrated adaptive problem-solving.

---

## Architecture

### Pure Python Implementation (Project 10)

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   camera_capture   │ --> │  person_detector │ --> │notification_handler│
│   (libcamera CLI)  │     │    (MediaPipe)   │     │   (mock email)   │
│   640x480 @ 1fps   │     │   1 FPS limit    │     │   logging only   │
└─────────────────────┘     └──────────────────┘     └──────────────────┘
```

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| camera_capture.py | libcamera CLI (`cam`) | Direct camera capture |
| person_detector.py | MediaPipe Pose | Person detection |
| notification_handler.py | Python logging | Mock email alerts |
| surveillance_node.py | Python threading | Orchestration |

### Hardware Verified

The system successfully detected the Raspberry Pi camera:

```
Available cameras
-----------------
0 : imx219 [3280x2464 10-bit RGGB] (/base/soc/i2c0mux/i2c@1/imx219@10)
    Modes: 'SRGGB10_CSI2P' : 640x480 [103.33 fps]
                             1640x1232 [41.85 fps]
                             1920x1080 [47.57 fps]
                             3280x2464 [21.19 fps]
```

---

## What Worked

### 1. Autonomous Decision-Making

GLM-5 didn't get stuck when ROS2 failed—it pivoted. This shows:
- **Problem recognition:** Identified the camera wasn't accessible via ROS
- **Alternative finding:** Found libcamera CLI as workaround
- **Execution:** Built working prototype without human intervention

### 2. Complete Pipeline Testing

Unlike other models, GLM-5 actually ran the full pipeline:
- ✅ Camera detection worked
- ✅ Image capture worked  
- ✅ MediaPipe model loaded
- ✅ Detection ran at 1 FPS
- ✅ Captured test images (test_capture.jpg, test_detection.jpg)

### 3. Cost Efficiency

At approximately **$0.27 per session**, GLM-5 was dramatically cheaper than Claude 4.6 (~$8.00) while delivering functional code.

### 4. Logging Structure

Implemented comprehensive logging:
```
logs/
├── surveillance.log      # Main application log
├── notifications.log     # Detection events
└── emails/               # Mock email records
    └── email_2025-02-18T10-30-45-123456.txt
```

---

## What Didn't Work

### 1. Framework Consistency

The core requirement was ROS2 development. Pure Python violated this:
- No ROS2 nodes
- No topic-based communication
- No rclpy/rclcpp patterns

### 2. Incremental Commits

GLM-5 forgot to commit throughout development:
- All changes pushed in one batch at the end
- No intermediate checkpoints
- Harder to trace decision process

### 3. Coming Back to User

Like Kimi, GLM-5 sometimes "forgot" to report back:
- Ran long operations without updates
- Required prompting for status

### 4. Long-Horizon Stability

Sessions occasionally hung during extended testing:
- 12-second run: captured fine
- 53-second run: captured fine  
- 7.6-second run: captured fine

But the overall session management was less robust than Claude.

---

## The Trial-2 Pivot (Project 11)

After this project, a second attempt (project 11-camera-surveillance-glm-5-trial-2) successfully converted the approach to ROS2:

### ROS2 Architecture (Trial-2)

```
┌─────────────┐     /camera/image_raw     ┌──────────────────┐     /detection/person     ┌──────────────────┐
│  camera_ros │ ───────────────────────> │  detector_node   │ ───────────────────────> │ notification_node│
│  (libcamera)│     sensor_msgs/Image    │  (MediaPipe)     │     std_msgs/String      │   (mock email)   │
└─────────────┘                          └──────────────────┘                           └──────────────────┘
```

This hybrid approach used:
- External `camera_ros` package for image capture
- Custom ROS2 nodes for detection and notification
- Proper topic remapping

---

## Cost Analysis

| Model | Cost per Session | Framework Adherence | Autonomy | Quality |
|-------|-----------------|---------------------|----------|---------|
| **Claude 4.6** | ~$8.00 | ✅ Excellent | Good | Excellent |
| **GLM-5** | ~$0.27 | ⚠️ Pivoted | Excellent | Good |
| **Kimi k2.5** | ~$2.00 | ⚠️ Struggled | Poor | Adequate |
| **Gemini-3-Flash** | ~$2.00 | ⚠️ Slow | Moderate | Adequate |

---

## Lessons Learned

### For Agentic Development

1. **Adaptability is valuable but must be constrained** — GLM-5's pivot worked functionally but violated project requirements
2. **Framework consistency matters** — ROS2 provides observability, testing, and modularity that pure Python lacks
3. **Cost ≠ quality** — The cheapest model pivoted autonomously; the most expensive maintained standards

### Technical Takeaways

1. **libcamera CLI works** — The `cam` command can capture images when ROS2 camera packages fail
2. **MediaPipe is reliable** — Pose detection works well on Raspberry Pi at 1 FPS
3. **Logging-first approach** — Structured logging made debugging possible even without ROS2 tools

---

## Conclusion

GLM-5's pure Python implementation was not what we asked for, but it worked. This highlights a fundamental tension in agentic development:

- **Constraint adherence** produces consistent, maintainable systems
- **Adaptive problem-solving** produces working systems, possibly in unexpected forms

For industrial applications, we need constraint adherence. For exploratory research, adaptability is valuable.

The follow-up trial-2 project showed that GLM-5 *could* produce ROS2 code when guided properly—but the original pivot, while non-compliant, proved the system's resilience.

---

## Project Artifacts

- **Location:** `~/.openclaw/openclaw-ros/projects/10-camera-surveillance-glm-5/`
- **Test Images:** `test_capture.jpg`, `test_detection.jpg`
- **Captures:** `captures/` (empty—no actual detections during testing)
- **Logs:** `logs/surveillance.log`

---

*This blog post is part of the openclaw-ros project documenting our journey with AI-driven robotics development.*
