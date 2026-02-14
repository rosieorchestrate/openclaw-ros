#!/bin/bash
# 30s YOLO Benchmarking Script with Visual Debugging

PROJECT_DIR="/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector"
source /opt/ros/kilted/setup.sh
source $PROJECT_DIR/src/yolo_detector/install/setup.sh

echo "Starting 30-second YOLO visual audit run..."

# Run camera, detector, and logger in background
ros2 run camera_ros camera_node > /dev/null 2>&1 &
CAM_PID=$!

ros2 run yolo_detector detector --ros-args -p model_path:=$PROJECT_DIR/config/models/yolo.weights -p config_path:=$PROJECT_DIR/config/models/yolo.cfg -p classes_path:=$PROJECT_DIR/config/models/coco.names -p confidence_threshold:=0.2 > /dev/null 2>&1 &
DET_PID=$!

ros2 run yolo_detector logger --ros-args -p log_dir:=$PROJECT_DIR/logs > /dev/null 2>&1 &
LOG_PID=$!

echo "Nodes started. Capturing frames and detections for 30 seconds..."
sleep 30

echo "Test complete. Stopping nodes..."
kill $CAM_PID $DET_PID $LOG_PID
sleep 2
echo "Cleanup finished."
