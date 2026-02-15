#!/bin/bash
# 30s Surveillance Pipeline Test

REPO_ROOT="/home/opencw/.openclaw/openclaw-ros"
PROJECT_DIR="$REPO_ROOT/projects/05_camera_surveillance"

source /opt/ros/kilted/setup.sh
source "$REPO_ROOT/projects/04_yolo_detector/src/yolo_detector/install/setup.sh"
source "$PROJECT_DIR/src/surveillance_logic/install/setup.sh"

echo "ROSIE: Initializing Surveillance Pipeline..."
echo "ROSIE: Triggering system for 30 seconds."

# Start the full stack
ros2 launch surveillance_logic simulation.launch.py > /dev/null 2>&1 &
STACK_PID=$!

sleep 30

echo "ROSIE: Test window closed. Shutting down..."
kill $STACK_PID
sleep 2

echo "ROSIE: Testing logic... Checking for mocked emails."
ls -la "$PROJECT_DIR/logs/emails/"
echo "ROSIE: Checking for evidence captures."
ls -la "$PROJECT_DIR/logs/temp_captures/"
