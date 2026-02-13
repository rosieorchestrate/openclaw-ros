# Sim-to-Real Success: Headless Camera Capture Milestone

**Authors:** Noah, Jakub, and Rosie (the ROS Orchestrator)  
**Date:** 2026-02-13

### TL;DR
We successfully implemented and deployed a ROS 2 camera capture system, transitioning seamlessly from a synthetic "Level 2" simulation to physical hardware. By rigorously verifying our logic against a digital twin first, we achieved a first-time success on the Raspberry Pi with the physical IMX219 sensor, capturing high-resolution images triggered via ROS topics.

### Goal
The mission was to build a robust `camera_capture` application. The requirements were strict: the system must handle high-bandwidth image streams, respond to asynchronous "capture" requests, and store images with unique timestamps—all while maintaining the engineering standards defined in our Contracts.

### The Phases of Development

#### Phase 1: Digital Twin (Simulation Level 2)
We began by creating a `virtual_camera` node. This node emulated real sensor behavior by publishing synthetic color-bar patterns with embedded ROS timestamps to `/camera/image_raw`. This allowed us to verify the `image_saver` logic—ensuring it could "catch" a frame and write it to disk—without needing physical access to the Pi's camera.

#### Phase 2: Headless Logic Verification
Using our previously established **Xvfb virtual display** and `ros2 topic pub` triggers, we proved the application worked in a completely headless server environment. We verified a stable 10Hz simulated stream and confirmed that files were being correctly written to our project's designated `/captures` folder.

#### Phase 3: Hardware Integration (The "Real" Test)
We swapped the `virtual_camera` for the real `camera_ros` node. The Raspberry Pi successfully registered the **IMX219 (/base/soc/i2c0mux/i2c@1/imx219@10)** sensor. Despite initial kernel-level "IPA module" warnings, we achieve a stable **14 Hz** physical stream. A mission-critical trigger was sent, and the system captured its first "real-world" frame.

### Results
- ✅ **Simulation Proof**: Logic verified via synthetic data.
- ✅ **Hardware Success**: Real-time IMX219 stream at 800x600 resolution.
- ✅ **Observability**: Every save event was logged with `key=value` precision.
- ✅ **Artifact**: Physical image successfully retrieved and shared via Telegram.

### Conclusion
This milestone confirms that our **Sim-to-Real** methodology is working. By separating logical verification from hardware constraints, we significantly reduced the complexity of debugging physical components. We learned that ROS 2's QoS policies (specifically the move to `BEST_EFFORT` for raw video) are critical for physical stability. **Next step:** Moving toward Phase 4—implementing vision-based detection logic!
