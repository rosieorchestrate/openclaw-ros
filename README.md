# OpenClaw ROS

A collaborative ROS 2 workspace on the Raspberry Pi 4, maintained by Noah, Jakub, and Rosie (the OpenClaw ROS Orchestrator). The goal is to progressively build increasingly complex ROS applications autonomously.

## Goal

Learn and validate ROS 2 development practices in a real hardware environment, using full AI orchestration to investigate how well OpenClaw can work in an incremental, observable, and reproducible way.

## Publications:

1. [Giving OpenClaw the Keys to Robotics: Agentic ROS on a Raspberry Pi](https://ai-at-the-edge.hashnode.dev/agentic-ros-openclaw-raspberry-pi#acknowledgments)

## Structure

```
/projects       ROS 2 packages, experiments, and iterations
/blogs          Milestone writeups documenting progress and decisions
/skills         Reusable agent skills (contract guard, simulation, diagnostics, etc.)
```

Supporting contracts define how the workspace operates:

- [DEVELOPMENT_CONTRACT.md](DEVELOPMENT_CONTRACT.md) — rules for incremental, reviewable progress
- [INTERFACES.md](INTERFACES.md) — canonical ROS topic/service interface definitions
- [OBSERVABILITY_CONTRACT.md](OBSERVABILITY_CONTRACT.md) — logging and status conventions
- [SIMULATION_CONTRACT.md](SIMULATION_CONTRACT.md) — simulation-vs-hardware parity rules
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md) — acceptance criteria and test standards

## Environment

- **Hardware**: Raspberry Pi 4 (8GB)
- **OS**: Ubuntu 24.04 (Noble)
- **ROS 2 Distro**: Kilted

---
*Created and maintained by Rosie via OpenClaw.*
