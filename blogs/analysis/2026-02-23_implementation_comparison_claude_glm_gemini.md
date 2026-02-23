# Camera Surveillance Implementation Comparison: Claude Opus 4.6 vs GLM5 vs Gemini-3-Flash

**A detailed analysis of ROS2 application implementations produced by different AI models**

**Date:** 2026-02-23
**Projects analyzed:**
- `projects/06_camera_surveillance` (Gemini-3-Flash)
- `projects/07-camera-surveillance-opus-4-6` (Claude Opus 4.6)
- `projects/11-camera-surveillance-glm-5-trial-2` (GLM5)

---

## TL;DR

**Architecture Choices:**
- Claude designed the most modular system with 4 separate nodes, including a dedicated throttling node to decouple camera frame rate from detection rate. This separation of concerns made the system easier to debug and extend.
- GLM5 built a lean 2-node system with graceful degradation—if MediaPipe failed to load, it automatically fell back to Haar cascade detection.
- Gemini produced the simplest working solution but with hardcoded paths and no fallback mechanisms.

**Deployment Maturity:**
- Claude implemented staggered node startup (camera first, then capture after 3s, then detection after 5s) to handle initialization dependencies—a pattern common in production ROS systems.
- GLM5 created the most configurable launch file with 8 runtime parameters, allowing tuning without code changes.
- Gemini's launch file started all nodes simultaneously with minimal parameters.

**Logging & Observability:**
- Claude logged to date-partitioned files (`alerts_2026-02-20.log`) plus machine-readable JSONL, tracking metrics like inference time and suppressed alert counts.
- GLM5 created individual files per detection event—more granular but harder to trace across sessions.
- Gemini used a single consolidated log file with plain text output.

**Code Quality Signals:**
- Claude included type hints, docstrings, QoS profiles for sensor reliability, and prepared hooks for real email sending (`mock_mode` parameter).
- GLM5 used modern Python idioms (`pathlib`, comprehensive docstrings) and defensive programming with explicit fallbacks.
- Gemini wrote procedural, inline code that worked but lacked abstraction or error recovery.

**Bottom line:** The code each model produced reflected its reasoning capabilities. Claude "thought" like a systems engineer; GLM5 prioritized robustness; Gemini solved the immediate problem without looking ahead.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [ROS Application Architecture](#1-ros-application-architecture)
3. [Topic Interfaces](#2-topic-interfaces)
4. [Deployment Strategy](#3-deployment-strategy)
5. [Logging Strategies](#4-logging-strategies)
6. [Coding Philosophy Comparison](#5-coding-philosophy-comparison)
7. [Detection Implementation Comparison](#6-detection-implementation-comparison)
8. [Summary of Strengths & Weaknesses](#7-summary-of-strengths--weaknesses)
9. [Conclusion](#conclusion)

---

## Overview

| Aspect | Project 06 (Gemini) | Project 07 (Claude Opus 4.6) | Project 11 (GLM5) |
|--------|---------------------|------------------------------|-------------------|
| **Nodes** | 3 (camera, detector, notifier) | 4 (camera, throttle, detector, alert) | 2 + external camera |
| **Detection Model** | MediaPipe Pose | MobileNet-SSD (Caffe) | MediaPipe Pose + Haar fallback |
| **Package Structure** | ROS2 ament_python | Standalone scripts | ROS2 ament_python |
| **Lines of Code** | ~175 | ~400 | ~420 |
| **Configurability** | Low | Medium | High |

---

## 1. ROS Application Architecture

### Project 06 (Gemini-3-Flash)
```
camera_node → /camera/image_raw → detector_node → /detections → mock_notifier
```
- **Simplest architecture**: 3 tightly-coupled nodes
- Camera node built from scratch using OpenCV `VideoCapture`
- Rate limiting handled *inside* the detector via timestamp comparison
- Single responsibility per node but minimal separation of concerns

### Project 07 (Claude Opus 4.6)
```
camera_ros → /camera/image_raw → camera_capture_node → /surveillance/throttled_image
                                                      ↓
                                      person_detector_node → /surveillance/detection
                                                           ↓
                                                      alert_node
                                                           ↓
                                       /surveillance/annotated_image (published back)
```
- **Most modular**: 4 nodes with clear separation
- Dedicated throttling node (`camera_capture_node`) decouples camera rate from detection rate
- Publishes annotated images back to the ROS graph for downstream consumers
- Uses external `camera_ros` package rather than reimplementing camera capture

### Project 11 (GLM5)
```
camera_ros → /camera/image_raw → detector_node → /detection/person → notification_node
```
- **Lean architecture**: 2 custom nodes + external camera
- Rate limiting handled inside detector node
- No intermediate throttling topic
- Most similar to Project 06 but with better fallback handling

---

## 2. Topic Interfaces

| Project | Topics Published | Message Type |
|---------|-----------------|--------------|
| **06** | `/camera/image_raw`, `/detections` | `Image`, `String` |
| **07** | `/camera/image_raw`, `/surveillance/throttled_image`, `/surveillance/detection`, `/surveillance/annotated_image` | `Image`, `Image`, `String (JSON)`, `Image` |
| **11** | `/camera/image_raw`, `/detection/person` | `Image`, `String (JSON)` |

**Key differences:**
- **Project 07** introduces namespaced topics (`/surveillance/*`) for clarity
- **Project 07** publishes annotated images as a separate topic—useful for visualization/debugging
- **Project 06** uses simple string messages; **07** and **11** use structured JSON

---

## 3. Deployment Strategy

### Project 06 (Gemini)
```python
# Simple simultaneous launch
Node(package='surveillance_system', executable='detector_node', ...)
Node(package='surveillance_system', executable='mock_notifier', ...)
```
- **Standard ROS2 launch**: All nodes start simultaneously
- Parameters hardcoded or minimal
- No startup sequencing consideration

### Project 07 (Claude Opus 4.6)
```python
# Staggered launch with TimerActions
TimerAction(period=3.0, actions=[ExecuteProcess(cmd=['python3', 'camera_capture_node.py', ...])])
TimerAction(period=5.0, actions=[ExecuteProcess(cmd=['python3', 'person_detector_node.py', ...])])
```
- **Staggered startup**: Camera first, then capture (3s delay), then detector/alert (5s delay)
- Uses `ExecuteProcess` instead of `Node`—runs standalone scripts rather than installed packages
- Path resolution done at launch time via `os.path` manipulation
- Most operationally aware of startup timing issues

### Project 11 (GLM5)
```python
# Parameterized launch with LaunchConfigurations
DeclareLaunchArgument('confidence_threshold', default_value='0.5', ...)
Node(..., parameters=[{'confidence_threshold': LaunchConfiguration('confidence_threshold')}])
```
- **Most configurable**: 8 launch arguments for runtime customization
- Proper ROS2 `LaunchConfiguration` substitutions
- No staggered timing, but parameters allow tuning without code changes

---

## 4. Logging Strategies

### Project 06 (Gemini)
```python
# Single consolidated log file
self.log_file = os.path.join(self.log_dir, 'email_mocks.log')
with open(self.log_file, 'a') as f:
    f.write(content)
```
- **Single file**: `logs/email_mocks.log`
- Plain text format with simple email mock structure
- No structured data export

### Project 07 (Claude Opus 4.6)
```python
# Date-partitioned logs + JSON events
log_filename = f'alerts_{log_date}.log'
events_log = os.path.join(self.logs_dir, f'detection_events_{log_date}.jsonl')
```
- **Dual logging**: Human-readable `.log` + machine-parseable `.jsonl`
- Date-partitioned files (e.g., `alerts_2026-02-20.log`)
- Tracks suppressed alerts: `suppressed_count` counter
- Rich metadata in JSON: detection ID, inference time, bounding boxes

### Project 11 (GLM5)
```python
# Per-event files + consolidated log
email_path = self.email_dir / f"email_{timestamp}.txt"
json_path = self.email_dir / f"detection_{timestamp}.json"
self.notification_log = self.log_dir / 'notifications.log'
```
- **Granular files**: Each detection gets its own `.txt` and `.json` file
- Consolidated summary in `notifications.log`
- Uses `pathlib.Path` (modern Python) vs `os.path` (traditional)

### Logging Comparison Table

| Aspect | Project 06 | Project 07 | Project 11 |
|--------|------------|------------|------------|
| Files per day | 1 | 2 | N×2 + 1 |
| Format | Plain text | Text + JSONL | Text + JSON |
| Traceability | Low | High | Medium |
| Storage efficiency | High | High | Low |

---

## 5. Coding Philosophy Comparison

### Project 06 (Gemini) — **Minimal & Direct**

```python
def listener_callback(self, msg):
    current_time = time.time()
    if current_time - self.last_detection_time < self.interval:
        return
    # ... detection logic inline
```

**Characteristics:**
- Procedural style with minimal abstraction
- Inline logic—everything in one method
- Hardcoded paths: `/home/opencw/.openclaw/openclaw-ros/projects/06_camera_surveillance/captures`
- No docstrings on classes/methods
- Uses `time.time()` for timing (system clock)
- No error recovery or fallback mechanisms
- Basic parameter usage with verbose getter chains:
  ```python
  self.get_parameter('detection_interval').get_parameter_value().double_value
  ```

### Project 07 (Claude Opus 4.6) — **Enterprise & Modular**

```python
def _build_email(self, detection: dict) -> dict:
    """Build email content from detection event."""
    # ... structured email building

def _mock_send(self, email: dict, detection: dict):
    """Mock email: print to terminal and log to file."""
    # ... separated concerns

def _real_send(self, email: dict, detection: dict):
    """Real email sending via SMTP — placeholder for future."""
    pass
```

**Characteristics:**
- **Clear separation of concerns**: `_build_email`, `_mock_send`, `_real_send` as separate methods
- Type hints on method signatures: `def detection_callback(self, msg: String):`
- Docstrings on every file and class
- Shebang and module docstrings: `#!/usr/bin/env python3\n""" ... """`
- Uses QoS profiles for sensor data reliability
- Operational metrics: tracks `suppressed_count`, logs inference time
- Prepares for production: `mock_mode` parameter, staggered launch timing
- Emoji usage in logs: `🚨 PERSON DETECTED`, `📧 MOCK EMAIL`
- More defensive coding with explicit bounds clamping:
  ```python
  x1, y1 = max(0, x1), max(0, y1)
  x2, y2 = min(w, x2), min(h, y2)
  ```

### Project 11 (GLM5) — **Defensive & Extensible**

```python
def _load_detector(self):
    """Load MediaPipe pose detection model."""
    try:
        import mediapipe as mp
        # ...
    except Exception as e:
        self.get_logger().warn(f'Could not load MediaPipe: {e}')
        self._load_haar_fallback()
```

**Characteristics:**
- **Graceful degradation**: Falls back to Haar cascades if MediaPipe unavailable
- Uses modern Python: `pathlib.Path`, f-strings throughout, `from datetime import datetime`
- Cleaner parameter access: `self.get_parameter('confidence_threshold').value`
- Comprehensive class docstrings with parameter documentation:
  ```python
  """
  Parameters:
      confidence_threshold: Minimum confidence for detection (default: 0.5)
      detection_rate: Detection frequency in Hz (default: 1.0)
  """
  ```
- Uses ROS clock for timing: `self.get_clock().now().nanoseconds / 1e9`
- Imports `logging` module (though not fully utilized)
- Model complexity awareness: `model_complexity=0` for Pi optimization
- Explicit detection structure with labeled fields:
  ```python
  {'bbox': [...], 'confidence': float, 'label': 'person'}
  ```

---

## 6. Detection Implementation Comparison

| Aspect | Project 06 | Project 07 | Project 11 |
|--------|------------|------------|------------|
| **Model** | MediaPipe Pose | MobileNet-SSD | MediaPipe Pose |
| **Fallback** | None | None | Haar cascades |
| **Input size** | Native | 300×300 (resized) | Native |
| **Inference timing** | Not tracked | Logged (ms) | Not tracked |
| **Confidence handling** | MediaPipe default | Explicit threshold filter | Aggregated from landmarks |
| **Bounding box source** | MediaPipe landmarks | DNN output | Computed from landmarks |
| **Annotation style** | MediaPipe drawing utils | Manual cv2 rectangle | Manual cv2 rectangle |

---

## 7. Summary of Strengths & Weaknesses

### Project 06 (Gemini)
| Strengths | Weaknesses |
|-----------|------------|
| Simplest to understand | Hardcoded paths |
| Fastest to deploy | No fallback mechanisms |
| | Limited configurability |

### Project 07 (Claude Opus 4.6)
| Strengths | Weaknesses |
|-----------|------------|
| Most production-ready architecture | More complex deployment (standalone scripts) |
| Best logging and observability | Higher initial setup overhead |
| Modular node separation (throttling decoupled) | |
| Prepared for real email sending | |

### Project 11 (GLM5)
| Strengths | Weaknesses |
|-----------|------------|
| Best fallback handling (Haar cascade backup) | Per-event file logging creates many small files |
| Most configurable launch file | Less operational metrics than Claude's version |
| Modern Python idioms | |
| Proper ROS2 package structure | |

---

## Conclusion

**Claude Opus 4.6** produced the most architecturally mature solution with clear separation of concerns, production-ready patterns (staggered startup, QoS profiles, dual logging), and forward-thinking design (mock mode toggle, annotated image republishing).

**GLM5** prioritized robustness through fallback detection and modern Python practices, with the most flexible launch configuration. It's the best balance of code quality and maintainability.

**Gemini-3-Flash** produced a working but minimal solution—suitable for prototyping but requiring significant hardening for production use.

The code each model produced directly reflects its reasoning capabilities: Claude approached the problem like a systems engineer planning for production; GLM5 thought defensively about failure modes; Gemini focused on getting the immediate task done.
