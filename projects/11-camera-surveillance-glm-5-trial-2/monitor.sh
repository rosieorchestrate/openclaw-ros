#!/bin/bash
# Resource monitoring script for surveillance system
# Runs for 10 minutes, sampling every 30 seconds

LOG_FILE="$HOME/.openclaw/openclaw-ros/projects/11-camera-surveillance-glm-5-trial-2/logs/monitoring.log"
DURATION=600  # 10 minutes in seconds
INTERVAL=30   # Sample every 30 seconds
SAMPLES=$((DURATION / INTERVAL))

echo "========================================" | tee -a "$LOG_FILE"
echo "Surveillance System Monitoring" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Duration: ${DURATION}s, Interval: ${INTERVAL}s" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Source ROS2
source /opt/ros/kilted/setup.bash

# Get PIDs of surveillance processes
get_pids() {
    pgrep -f "camera_node|detector_node|notification_node" | tr '\n' ','
}

# Monitor function
monitor() {
    local sample=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "" | tee -a "$LOG_FILE"
    echo "--- Sample $sample/$SAMPLES at $timestamp ---" | tee -a "$LOG_FILE"
    
    # CPU and Memory for surveillance processes
    echo "Process Resources:" | tee -a "$LOG_FILE"
    ps aux | grep -E "camera_node|detector_node|notification_node" | grep -v grep | awk '{printf "  %-20s CPU: %5s%%  MEM: %5s%%  RSS: %s KB\n", $11, $3, $4, $6}' | tee -a "$LOG_FILE"
    
    # Overall system stats
    echo "System Resources:" | tee -a "$LOG_FILE"
    echo "  Load Avg: $(cat /proc/loadavg | awk '{print $1", "$2", "$3}')" | tee -a "$LOG_FILE"
    echo "  Memory: $(free -m | awk '/Mem:/{printf "Used: %dMB / %dMB (%.1f%%)", $3, $2, ($3/$2)*100}')" | tee -a "$LOG_FILE"
    
    # CPU temperature (Raspberry Pi)
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        echo "  CPU Temp: $((temp/1000))°C" | tee -a "$LOG_FILE"
    fi
    
    # ROS2 topic hz (sample for 5 seconds)
    echo "ROS2 Topic Rates (5s sample):" | tee -a "$LOG_FILE"
    
    # Check if topics are publishing
    hz_camera=$(timeout 6 ros2 topic hz /camera/image_raw 2>&1 | tail -1)
    echo "  /camera/image_raw: $hz_camera" | tee -a "$LOG_FILE"
    
    # Detection count
    detection_count=$(ls -1 $HOME/.openclaw/openclaw-ros/projects/11-camera-surveillance-glm-5-trial-2/captures/ 2>/dev/null | wc -l)
    echo "  Detections saved: $detection_count" | tee -a "$LOG_FILE"
}

# Run monitoring loop
for i in $(seq 1 $SAMPLES); do
    monitor $i
    if [ $i -lt $SAMPLES ]; then
        sleep $INTERVAL
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Monitoring Complete: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"