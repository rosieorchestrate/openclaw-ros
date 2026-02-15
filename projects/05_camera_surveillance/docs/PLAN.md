# Plan: Camera-Based Surveillance (Milestone 1)
Last Updated: 2026-02-15

## Objective
Implement a surveillance system that detects people at 1Hz and triggers an email alert (mocked) with the corresponding image.

## Roadmap
- [ ] **Step 1: Interface Definition**: 
  - Update `INTERFACES.md` with surveillance-specific topics.
- [ ] **Step 2: Project & Package Initialization**:
  - Create the `surveillance_logic` package.
- [ ] **Step 3: Logic Node Implementation**:
  - `surveillant`: Monitors `/detections`, filters for "person", triggers alert.
  - `email_mocker`: Subscribes to alert, writes email body to `logs/emails/`.
- [ ] **Step 4: Simulation Level 2 (Real Processing + Mock Actuator)**:
  - Verify detection-to-email flow using pre-recorded or synthetic data.
- [ ] **Step 5: Hardware Integration**:
  - Connect to live IMX219 sensor.
- [ ] **Step 6: User Verification**:
  - Provide `tests/test_surveillance_pipeline.sh`.

## Simulation Strategy
- **Level**: 2 (Real Processing Logic).
- **Backend**: Reuse YOLO detector from Project 04.
- **Mock**: Email node writes to local text files instead of SMTP.
