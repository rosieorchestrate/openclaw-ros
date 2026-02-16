#!/bin/bash
# ============================================================
# Stop Surveillance System
# ============================================================
# Kills all surveillance-related ROS2 nodes gracefully.
#
# Usage: ./scripts/stop.sh
# ============================================================

echo "🛑 Stopping surveillance system..."

# Kill known node processes
pkill -f "camera_capture_node.py" 2>/dev/null && echo "  Stopped: camera_capture_node" || true
pkill -f "person_detector_node.py" 2>/dev/null && echo "  Stopped: person_detector_node" || true
pkill -f "alert_node.py" 2>/dev/null && echo "  Stopped: alert_node" || true
pkill -f "snapshot_node.py" 2>/dev/null && echo "  Stopped: snapshot_node" || true
pkill -f "camera_node.*surveillance" 2>/dev/null && echo "  Stopped: camera_node" || true

# Also kill any ros2 launch process for this project
pkill -f "surveillance_launch.py" 2>/dev/null && echo "  Stopped: launch process" || true

echo ""
echo "✅ All surveillance nodes stopped."
