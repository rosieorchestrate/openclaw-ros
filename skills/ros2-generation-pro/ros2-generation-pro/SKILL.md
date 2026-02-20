---
name: ros2-generation-pro
description: Build robust, hardware-aware ROS 2 nodes with lifecycle management and safety wrappers. Use when creating new ROS 2 packages or Python nodes that interface with hardware (GPIO, CSI-Camera, I2C) to ensure resource cleanup and CPU efficiency.
---

# Pro-Level ROS 2 Generation

This skill ensures every node created is clean, tidy, and production-ready for Raspberry Pi environments.

## Non-Negotiable Rules

1. **The Rosdep Guard**: Never build without running `rosdep install --from-paths src --ignore-src -y`.
2. **The 80% Rule**: On Pi hardware, nodes must monitor their loop frequency. If internal processing consumes >80% of the timer window, log a Warning.
3. **Graceful Exit**: Every Python node **MUST** use a `try-finally` block to ensure GPIO/Camera resources are explicitly released on shutdown.

## Protocol

### Step 1: Dependencies
Resolve dependencies before generating code. If hardware libraries (like `libcamera`) are missing, fail or install them first.

### Step 2: The Safety Wrapper (Python)
Use the template in `assets/python_node_template.py` as the base.
- Hardware pins/IDs must be **parameters**.
- Use `qos_profile_sensor_data` for cameras/high-bandwidth sensors.

### Step 3: Timers vs sleep()
Never use `time.sleep()`. Always use `self.create_timer(1.0/freq, callback)`.

### Step 4: Build & Register
Build with symlinks to allow live code edits:
```bash
colcon build --symlink-install
```

### Step 5: The "Pulse" Test
Verify the node is alive and healthy:
1. Start node in background.
2. Run `ros2 topic bw /topic_name` for 2 seconds.
3. **Pass Criteria**: Stable bandwidth > 0.

## Implementation Details

- **QoS**: Use `sensor_data` for high-bandwidth/unreliable links; `reliable` for commands.
- **Hardware Cleanup**: Ensure `node.destroy_node()` and `rclpy.shutdown()` are called.
