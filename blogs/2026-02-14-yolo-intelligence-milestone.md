# Artificial Intelligence on the Edge: The YOLO Detection Milestone

**Authors:** Noah, Jakub, and Rosie (the ROS Orchestrator)  
**Date:** 2026-02-14

### TL;DR
We successfully integrated local, real-time object detection into our ROS 2 environment using YOLOv4-tiny. By implementing a throttled 1Hz inference pipeline, we achieved stable intelligent vision on the Raspberry Pi 4, complete with conditional visual debugging and high-rigor structured tracing for headless logic auditing.

### Goal
The plan was to move from simple image capture to active perception. We required a system capable of analyzing the physical world locally on the Pi, identifying objects, and maintaining a persistent log of detections (label, confidence) without overloading the CPU.

### Technical Challenges & Solutions

#### 1. The Power-to-Processing Balance
The Pi 4, while capable, cannot perform deep learning inference at the full 14Hz frame rate of the camera. To respect our **80% Performance Rule**, we implemented a **Throttled 1Hz Timer Pattern**. This ensures the node samples exactly one high-quality frame per second, leaving ample resources for other robotics tasks.

#### 2. Conditional Observability
To avoid repository bloat while ensuring logic verification, we implemented a **`save_debug_images` flag**. When toggled, the system draws detections directly onto frames and archives them; in production mode, it remains a silent, data-only background auditor.

#### 3. High-Rigor Tracing
We utilized the ROS 2 **DEBUG level logging** to track the behavior of the neural network. This allows us to see exactly when inference starts, why it might skip a frame, and the raw confidence scores of every identified candidate before they hit the filtered logs.

### Results
- ✅ **Local Inference**: YOLOv4-tiny running locally via OpenCV DNN.
- ✅ **Stable Sampling**: 1Hz processing loop verified via internal frequency analysis (1.4Hz raw capability).
- ✅ **Traceability**: Successful detection of a `mouse` (conf: 0.23) logged with high-precision timestamps.
- ✅ **Headless Validation**: Verified the entire vision stack headlessly using Xvfb and automated audit scripts.

### Conclusion
This project marks a fundamental shift in our workshop: we have evolved from a "connected camera" to an **Intelligent Agent**. We learned that edge AI requires strict sampling discipline to maintain system health. With the detection pipeline now production-ready,เรา are poised to begin building autonomous logic that reacts to what the Pi "sees." **Next up:** Behavioral decision trees based on visual input.
