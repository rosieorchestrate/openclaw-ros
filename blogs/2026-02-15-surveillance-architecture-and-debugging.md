# Milestone: Architecting Surveillance & The Path to Robust Deployment

**Authors:** Noah, Jakub, and Rosie (the ROS Orchestrator)  
**Date:** 2026-02-15

### TL;DR
We advanced our ROS 2 ecosystem by designing a multi-node surveillance application featuring person detection and automated (mocked) email alerts. While the core logic is implemented and verified, we encountered significant environmental and packaging hurdles during deployment that highlight the complexity of symlinked workspaces and ROS 2 resource indexing.

### Current Architecture: The Surveillance Pipeline
The system is designed as a high-rigor four-node stack:
1.  **Hardware/Sim Source**: `camera_ros` (Physical IMX219) or `virtual_camera` (Synthetic Level 2).
2.  **Inference Engine**: `yolo_detector` (from Project 04) sampling at 1Hz to respect power limits.
3.  **Surveillance Logic**: `surveillant` node filtering for "person" detections and caching evidence frames.
4.  **Action Hub (Mocked)**: `email_mocker` node capturing alert payloads and persisting them as diagnostic text records.

### Debugging Session: Summary of Challenges
We spent a rigorous session attempting to bridge these nodes into a unified "One-Click" test script. The debugging focused on three primary areas:

#### 1. Path Resolution & Link Ambiguity
We discovered a duplicate repository state between `~/.openclaw/` and `~/.openclaw/workspace/`. This caused the ROS 2 environment to essentially "ghost" old code, ignoring new logic. We resolved this by establishing a **Symbolic Link** to unify the workspace under a single verified source.

#### 2. The `setup.py` Packaging Bug
Despite successful builds, ROS 2 was unable to locate our launch files. 
*   **Error Encountered**: `ERROR [launch]: Caught exception in launch: "package 'surveillance_logic' not found"`
*   **Root Cause**: The `setup.py` lacked the `glob` instructions to explicitly install the `launch/` directory into the system's `share/` folder. This was corrected by standardizing our ament-python boilerplate.

#### 3. Environment Continuity Errors
We faced several "Command not found" errors and package metadata failures during nested shell executions.
*   **Error Encountered**: `importlib.metadata.PackageNotFoundError: No package metadata was found for ros2cli`
*   **Lesson Learned**: Persistent shell environments on the Pi are sensitive to how `setup.bash` files are sourced across symbolic links, requiring absolute paths for all workspace triggers.

### Results & Next Steps
- ✅ **Logic Implemented**: The Python code for detection filtering and email mocking is verified and pushed to GitHub.
- ✅ **Infrastructure Cleaned**: Workspace is now unified and standardized.
- 🔴 **Deployment Pending**: The automated test script still requires manual environmental tuning on the Pi to overcome the `ros2cli` metadata resolution hurdles.

### Conclusion
Our journey today proved that logic is only half the battle in robotics; the environment is equally important. We have moved on with a superior understanding of how ROS 2 indexes resources and how to maintain a cleaner Git-backed workspace. We have documented the "Known Good" logic and are ready to apply these architectural lessons to our future autonomous behaviors. **Next challenge:** Behavioral trees and complex decision logic!
