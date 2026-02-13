# Plan: Camera Capture (Milestone 1)
Last Updated: 2026-02-13

## Objective
Create a ROS 2 application that captures and saves an image from the camera upon a trigger (command).

## Roadmap
- [ ] **Step 1: Simulation Level 2 (Real Processing)**: 
  - Create a `virtual_camera` node that publishes synthetic image data.
  - Create a `image_saver` node that subscribes to images and a trigger topic.
- [ ] **Step 2: Logic Verification**:
  - Use `turtlesim` or simple CLI triggers to request a capture in simulation.
- [ ] **Step 3: Hardware Integration**:
  - Swap `virtual_camera` for `camera_ros`.
  - Handle physical storage into the project's data folder.

## Simulation Strategy
- **Level**: 2 (Real Processing / synthetic data)
- **Virtual Sensor**: `virtual_camera` emitting constant color or test patterns to `/camera/image_raw`.
- **Trigger**: `/capture_request` (std_msgs/Empty).
