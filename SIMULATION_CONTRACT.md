# Simulation Skill (ROS2)

## Purpose
Create a simulation that exercises the SAME ROS interfaces as the real system while replacing hardware with virtual components.

## Authority
**INTERFACES.md is law.** If simulation and code disagree → simulation is wrong.

## Core Rule: Interface Parity
Simulation MUST:
- publish/subscribe to the same topics/services/actions.
- use the same message types.
- expose the same parameters.
Simulation MUST NOT:
- rename interfaces or invent shortcuts.
- bypass decision logic or alter application behavior.

## Required Components
### 1. Virtual Sensor Backends
Publish to canonical topics in `INTERFACES.md`. Sources: prerecorded data, synthetic generation, or scripted events.
### 2. Virtual Actuator Backends
Subscribe to commands, NEVER access real hardware, and emit observable logs/status.
### 3. Scenario Driver
Control stimulus timing. Terminate or reach steady state in bounded time. Use exposed seeds for randomness.

## Observability (Mandatory)
Produce structured logs and publish status topics. Success/failure must be visible without GUIs (no mandatory RViz).

## Simulation Levels
- **Level 1 — Stub**: High-level signals injected.
- **Level 2 — Real Processing**: Realistic raw data, full application pipeline.
- **Level 3 — Disturbance**: Noise, delay, dropouts added.
Current level MUST be in `PLAN.md`.

## Deliverables
1. System launches.
2. Interfaces match `INTERFACES.md`.
3. Behavior is observable via logs/status.
4. Verification script exists.

## Failure Labels
SUCCESS, TIMEOUT, INVALID_COMMAND, NO_INPUT, COLLISION, OUT_OF_RANGE, DEVICE_UNAVAILABLE.

## Completion Rule
Milestone is complete ONLY IF: verification passes, interfaces remain compliant, and outcome is observable headlessly.
