#!/bin/bash
# ============================================================
# Quick Camera Snapshot
# ============================================================
# Takes a single frame from the camera and saves it.
# Can work with or without the surveillance system running.
#
# Usage:
#   ./scripts/snapshot.sh              # Auto-named with timestamp
#   ./scripts/snapshot.sh my_photo     # Custom name: my_photo.jpg
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SNAPSHOTS_DIR="$PROJECT_ROOT/captures/snapshots"

source /opt/ros/kilted/setup.bash
mkdir -p "$SNAPSHOTS_DIR"

CUSTOM_NAME="${1:-}"

echo "📸 Taking snapshot..."

# Check if camera topic is already publishing
if ros2 topic list 2>/dev/null | grep -q "/camera/image_raw"; then
    echo "   Camera topic found — using existing stream"
    
    if [ -n "$CUSTOM_NAME" ]; then
        python3 "$PROJECT_ROOT/nodes/snapshot_node.py" --ros-args \
            -p "project_root:=$PROJECT_ROOT" \
            -p "output_name:=${CUSTOM_NAME}.jpg"
    else
        python3 "$PROJECT_ROOT/nodes/snapshot_node.py" --ros-args \
            -p "project_root:=$PROJECT_ROOT"
    fi
else
    echo "   No camera topic — starting camera node for snapshot..."
    
    # Start camera node in background
    ros2 run camera_ros camera_node --ros-args -p width:=640 -p height:=480 -p camera:=0 &
    CAM_PID=$!
    
    # Wait for topic to appear
    echo "   Waiting for camera to start..."
    for i in $(seq 1 15); do
        if ros2 topic list 2>/dev/null | grep -q "/camera/image_raw"; then
            break
        fi
        sleep 1
    done
    
    sleep 1  # Extra settling time
    
    if [ -n "$CUSTOM_NAME" ]; then
        python3 "$PROJECT_ROOT/nodes/snapshot_node.py" --ros-args \
            -p "project_root:=$PROJECT_ROOT" \
            -p "output_name:=${CUSTOM_NAME}.jpg"
    else
        python3 "$PROJECT_ROOT/nodes/snapshot_node.py" --ros-args \
            -p "project_root:=$PROJECT_ROOT"
    fi
    
    # Clean up camera node
    kill $CAM_PID 2>/dev/null || true
    wait $CAM_PID 2>/dev/null || true
fi

echo ""
echo "📂 Snapshots saved in: $SNAPSHOTS_DIR"
ls -lt "$SNAPSHOTS_DIR" | head -5
