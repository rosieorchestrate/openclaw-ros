#!/bin/bash
# 05 Surveillance PRO Simulation Audit

REPO_ROOT="/home/opencw/.openclaw/openclaw-ros"
PROJECT_DIR="$REPO_ROOT/projects/05_surveillance_pro"

source /opt/ros/kilted/setup.sh
# Source P03 for virtual_camera logic
source "$REPO_ROOT/projects/03_camera_capture/src/camera_capture/install/setup.bash"
# Source P05 PRO for surveillance
source "$PROJECT_DIR/src/surveillance_logic/install/setup.bash"

echo "ROSIE SIM [PRO]: Initializing Environment..."

# 1. Virtual Camera
ros2 run camera_capture virtual_camera > /dev/null 2>&1 &
CAM_PID=$!

# 2. Logic node & Mock alert
ros2 launch surveillance_logic simulation.launch.py > /dev/null 2>&1 &
LOGIC_PID=$!

sleep 5
echo "ROSIE SIM [PRO]: Injecting synthetic 'person' detection..."
ros2 topic pub --once /detections vision_msgs/msg/Detection2DArray "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: 'camera_link'}, detections: [{results: [{hypothesis: {class_id: 'person', score: 0.99}}]}]}"

sleep 5
echo "ROSIE SIM [PRO]: Audit finished. Cleaning up..."
kill $CAM_PID $LOGIC_PID
pkill -f surveillance

echo ""
echo "ROSIE SIM [PRO]: Verification results in logs/emails/"
ls -la "$PROJECT_DIR/logs/emails/"
echo ""
echo "ROSIE SIM [PRO]: View contents:"
cat "$PROJECT_DIR/logs/emails/"email_record_*.txt
