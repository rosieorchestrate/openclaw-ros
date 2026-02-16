# Simulation & Verification: 06_camera_surveillance

## Verification Contract
- **Detections**: Must trigger exactly one mock email log per person detection.
- **Timing**: Detection loop must not exceed 1Hz.
- **Artifacts**: Frames must be saved to `captures/` folder with timestamped filenames.

## Simulation Setup
- Since this requires a physical camera, initial testing can use:
  - Static images published to the image topic.
  - Video file playback as a mock camera stream.
- The Notification Node will be verified by checking the existence of log files in the `logs/` directory.

## Testing Procedure
1. Launch the `mock_notifier` node.
2. Publish a test detection message to the `/detections` topic.
3. Verify terminal output message: "DETECTION: Person found. Mocking email to rosie.orchestrate@gmail.com".
4. Check `logs/email_mocks.log`.
