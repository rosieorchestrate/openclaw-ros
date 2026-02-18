#!/bin/bash
# Run the ROS2 surveillance system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source ROS2
source /opt/ros/kilted/setup.bash

# Build if needed
if [ ! -d "install" ]; then
    echo "Building workspace..."
    colcon build --symlink-install
fi

# Source workspace
source install/setup.bash

echo "=========================================="
echo "Starting ROS2 Surveillance System"
echo "=========================================="
echo "Camera: /camera/image_raw"
echo "Detection: /detection/person"
echo "Recipient: rosie.orchestrate@gmail.com"
echo "=========================================="
echo ""

# Launch the system
ros2 launch surveillance_ros surveillance.launch.py \
    captures_dir:="$SCRIPT_DIR/captures" \
    log_dir:="$SCRIPT_DIR/logs"