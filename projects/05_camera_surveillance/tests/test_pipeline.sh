#!/bin/bash
# 30s Surveillance Pipeline Test (Absolute Path Fix)

REPO_ROOT="/home/opencw/.openclaw/openclaw-ros"
PROJECT_DIR="$REPO_ROOT/projects/05_camera_surveillance"

source /opt/ros/kilted/setup.sh
# Final verified path to YOLO detector
source "$REPO_ROOT/projects/04_yolo_detector/src/yolo_detector/install/setup.bash"
# Final verified path to Surveillance Logic
source "$PROJECT_DIR/src/surveillance_logic/install/setup.bash"

echo "ROSIE: Initializing Surveillance Pipeline..."
echo "ROSIE: Ensure log directories exist..."
mkdir -p "$PROJECT_DIR/logs/emails" "$PROJECT_DIR/logs/temp_captures"
chmod -R 775 "$PROJECT_DIR/logs"

echo "ROSIE: Triggering system for 30 seconds."

# Start the full stack
ros2 launch surveillance_logic simulation.launch.py > /dev/null 2>&1 &
STACK_PID=$!

# Health check
sleep 2
if ! ps -p $STACK_PID > /dev/null; then
    echo "ERROR: ROS 2 Launch failed to start. Check if YOLO and Surveillance are built."
    exit 1
fi

sleep 28

echo "ROSIE: Test window closed. Shutting down..."
kill $STACK_PID
# Aggregate cleanup
pkill -9 -f 'surveillant'
pkill -9 -f 'email_mocker'
pkill -9 -f 'camera_node'
pkill -9 -f 'detector'

sleep 2

echo "ROSIE: Testing logic... Checking for mocked emails."
ls -la "$PROJECT_DIR/logs/emails/"
echo "ROSIE: Checking for evidence captures."
ls -la "$PROJECT_DIR/logs/temp_captures/"
