# The Blink-Talker Protocol: Our First ROS 2 Milestone

**Authors:** Noah, Jakub, and Rosie (the ROS Orchestrator)  
**Date:** 2026-02-11

### TL;DR
We successfully deployed a multi-node ROS 2 system on a Raspberry Pi using the "Kilted" distro. The project coordinates a random-interval talker with a logging listener that provides physical feedback via an LED on Pin 16. Despite starting as ROS 2 beginners, we established a robust workflow including automated discovery, safety-first code generation, and professional Git versioning.

### Goal
The plan was to move beyond simple scripts and build a coordinated ROS 2 system. We wanted a talker that sent messages at unpredictable intervals (0.5–3s) and a listener that could simultaneously log data to a local file and trigger a physical LED blink (0.3s).

*Side note: We are all navigating the ROS 2 learning curve together! This experiment was the ultimate test of Rosie’s ability to bridge high-level intent with low-level robotics execution.*

### Device Setup
- **Hardware**: Raspberry Pi 4 (8GB) with a red LED on Pin 16 (GPIO 16 / Physical 36).
- **OS/Software**: Ubuntu 24.04 (Noble) running ROS 2 "Kilted".
- **Initial State**: The system was missing critical build tools like `colcon` and faced several "GPIO busy" conflicts from legacy scripts. Rosie required a secure `sudo` configuration to manage system-level dependencies.

### The Journey: Experiments & Evolution

#### 1. The Skill Foundation
Before writing a single line of project code, we built three foundational "Skills":
- **`ros2-discovery`**: To map out the ecosystem.
- **`ros2-generation-pro`**: To ensure every node uses a "Safety Wrapper" (try-finally) to release hardware.
- **`ros2-diag-health`**: To monitor Pi thermals and power throttling.

#### 2. The Random Talker & Logging Listener
We ran into early trouble with `lgpio` and `/dev/mem` permissions, leading us to adopt `python3-gpiozero`. The breakthrough came when we synchronized three concurrent nodes:
- **`talker`**: Our random message generator.
- **`listener`**: Our "Data Hub" that writes to `logs/messages.log` and blinks the LED.
- **`terminal_listener`**: Our live monitor for debugging.

### Results
The system achieved full synchronization:
- ✅ **Messages**: Flowing at random 0.5–3s intervals.
- ✅ **Persistence**: Every message is timestamped and saved in the project folder.
- ✅ **Hardware**: The LED blinks exactly 0.3s for every packet received.

### Conclusion
This project proved that even for ROS 2 beginners, a structured engineering approach—specifically using "Safety Wrappers" and professional Git commits—prevents hardware deadlocks. We learned that `colcon build --symlink-install` is a game-changer for rapid Python development. The setup was occasionally finicky with GPIO permissions, but the move to `gpiozero` smoothed out the experience. Next up: we tackle the `libcamera` IPA errors to get our visual sensors online!
