---
name: ros2-diag-health
description: Identify why ROS 2 nodes are missing, hardware is unresponsive, or system performance is degraded. Triggers on user reports of "crashes," "slow data," "camera not working," or "node failed."
---

# ROS 2 System Diagnosis & Hardware Health

Use this skill to perform data-backed troubleshooting of the ROS 2 stack and the underlying Raspberry Pi hardware.

## Non-Negotiable Rules

1. **Trust no one**: An "Active" node status in `ros2 node list` is not proof of life. Verify message flow with `hz` or `bw`.
2. **Hardware First**: For hardware nodes (Camera, I2C, GPIO), always check `dmesg` for kernel/voltage errors before debugging code.
3. **No "Guessing"**: Use `ros2 doctor` and `vcgencmd` to provide evidence-backed diagnoses.

## Diagnostic Workflow

### Step 1: Software Health (The ROS 2 Layer)
Check for "Ghost Nodes" and communication silos:
- **Graph**: `ros2 node list` and `ros2 topic list`.
- **Integrity**: `ros2 doctor --report` (Check for middleware/RMW mismatches).
- **Flow**: Use `ros2 topic hz <topic>` for 5s. Frequency 0.0 = Deadlock.

### Step 2: Physical Health (The Pi Layer)
Identify environmental bottlenecks:
- **Thermal**: `vcgencmd measure_temp` (Limit: 80°C).
- **Power**: `vcgencmd get_throttled` (Critical for under-voltage detection).
- **Logs**: `dmesg | tail -n 50` (Look for V4L2, under-voltage, or I/O errors).

### Step 3: Deep Dive
If a specific node is failing:
- **Trace**: `export RCUTILS_LOG_LEVEL=DEBUG && ros2 run <pkg> <exe>`.
- **Dependencies**: `ldd` (C++) or `pip check` (Python).

## Required Output Format: The "Health Report"

Present findings in this structure:

| Category | Status | Details |
| :--- | :--- | :--- |
| **ROS2 Graph** | 🟢/🟡/🔴 | e.g., Node /camera_node missing. |
| **Hardware** | 🟢/🟡/🔴 | e.g., Under-voltage detected in dmesg. |
| **Resources** | 🟢/🟡/🔴 | e.g., 72°C - No Throttling. |

**Suggested Fix**: [Specific Action]
