# Plan: Surveillance Pro (Milestone 1)
Last Updated: 2026-02-15

## Objective
Rebuild a high-rigor, contract-compliant surveillance system from scratch.
Goal: Filter "person" detections @ 1Hz and trigger email alerts with image support.

## Roadmap
- [ ] **Step 1: Scaffolding (M1.1)**: Create ROS2 package `surveillance_logic` in `src/`.
- [ ] **Step 2: Logic Nodes (M1.2)**: 
    - `surveillant`: Filter 'person' + Image caching (high-rigor QoS).
    - `email_mocker`: Terminal audit + log persistence.
- [ ] **Step 3: Verification (M1.3)**: Integrated Level 2 Simulation (Virtual Camera ➡️ YOLO ➡️ Alerts).
- [ ] **Step 4: Real-World Audit (M1.4)**: Physical Pi 4 deployment.

## Simulation Level
- Level 2: Real Processing with synthetic image injection.
