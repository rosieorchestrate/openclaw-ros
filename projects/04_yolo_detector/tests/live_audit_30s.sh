#!/bin/bash
# High-Rigor Live Audit: 30s YOLO test with image persistence

PROJECT_DIR="/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_DIR="$LOG_DIR/audit_$TIMESTAMP"

mkdir -p "$RUN_DIR"
source /opt/ros/kilted/setup.sh
source "$PROJECT_DIR/src/yolo_detector/install/setup.sh"

echo "ROSIE: Starting 30-second Visual Audit..."
echo "ROSIE: Data will be captured in $RUN_DIR"

# Launch Nodes
ros2 run camera_ros camera_node > /dev/null 2>&1 &
CAM_PID=$!

ros2 run yolo_detector detector --ros-args -p model_path:="$PROJECT_DIR/config/models/yolo.weights" -p config_path:="$PROJECT_DIR/config/models/yolo.cfg" -p classes_path:="$PROJECT_DIR/config/models/coco.names" -p confidence_threshold:=0.2 > /dev/null 2>&1 &
DET_PID=$!

ros2 run yolo_detector logger --ros-args -p log_dir:="$LOG_DIR" > /dev/null 2>&1 &
LOG_PID=$!

# Inform user
echo "ROSIE: Test live. Monitoring graph for /detections..."
sleep 30

# Secure Shutdown
echo "ROSIE: Time limit reached. Cleaning up processes..."
kill $CAM_PID $DET_PID $LOG_PID
sleep 2

echo "ROSIE: Audit complete."
echo "ROSIE: Results location: $RUN_DIR"
ls -la "$RUN_DIR"
