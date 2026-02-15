# Plan: Camera-Based Surveillance (Milestone 1)
Last Updated: 2026-02-15

## Objective
Rebuild the surveillance system from scratch with absolute contract compliance.
Goal: Detect "person" @ 1Hz and trigger a mocked email alert with image caching.

## Roadmap
- [ ] **Step 1: Interface Compliance (M1.1)**: Verify/Update INTERFACES.md.
- [ ] **Step 2: Scaffolding (M1.2)**: Create `surveillance_logic` package with proper `setup.py` (fixed globbing).
- [ ] **Step 3: Logic Implementation (M1.3)**:
    - `surveillant`: Filter for 'person' + Image caching.
    - `email_mocker`: Terminal output + local file persistence.
- [ ] **Step 4: Logic Verification (M1.4)**: Integrated 30s Simulation Level 2 (Xvfb + Synthetic Triggers).
- [ ] **Step 5: Hardware Benchmark (M1.5)**: Physical IMX219 test.

## Simulation Level
- Level 2: Real Processing.
- Virtual Camera (synthetic data) ➡️ YOLO (local) ➡️ Surveillant ➡️ Email Mock.
