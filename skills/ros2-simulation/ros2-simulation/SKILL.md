---
name: ros2-simulation
description: Create and execute ROS 2 simulations with strict interface parity to real hardware. Enforces that virtual components use the same topics, types, and parameters as the production system. Use when testing logic without hardware or verifying scenarios headlessly.
---

# ROS 2 Simulation

## Authority: INTERFACES.md is Law
The simulation must be an exact digital twin of the system's ROS graph.

## ⛓️ Simulation & Knowledge Guard
- **Turtlesim Reference**: Use `turtlesim` for behavioral verification and sim-to-real plumbing tests. Consult [ROS2 Industrial Workshop](https://ros2-industrial-workshop.readthedocs.io/en/latest/_source/basics/ROS2-Filesystem.html) for canonical workspace navigation (underlay/overlay sourcing, `colcon` symlink builds).
- **Interface Parity**: Simulation must use the same topics, types, and parameters. No shortcuts.
- **Headless Validation**: Success/Failure must be visible via logs/status. RViz is optional.
- **Backend Selection**: Switch between Sim and Hardware via launch arguments or parameters.

## Component Strategy
1. **Virtual Sensors**: Publish raw data to canonical topics.
2. **Virtual Actuators**: Subscribe to commands and update status topics; do not touch hardware.
3. **Scenario Drivers**: Scripted events with bounded time and deterministic seeds.

## Simulation Levels
- **Level 1 (Stub)**: Signal injection.
- **Level 2 (Real)**: Full pipeline, realistic data.
- **Level 3 (Disturbance)**: Stress test (noise, delay).

## Execution Procedure
1. Launch Simulation.
2. Verify graph against `INTERFACES.md`.
3. Check `<node>/status` for digital health.
4. Run `scripts/run_acceptance_<name>.sh`. Exit 0 required.
