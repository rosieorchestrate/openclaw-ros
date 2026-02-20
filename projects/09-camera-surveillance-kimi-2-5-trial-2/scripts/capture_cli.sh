#!/bin/bash
# capture_cli.sh - Easy CLI for on-demand capture

set -e

source /opt/ros/kilted/setup.bash 2>/dev/null || {
    echo "ERROR: ROS2 not found"
    exit 1
}

CMD=${1:-help}

case "$CMD" in
    capture|cap|single)
        echo "📸 Capturing single frame..."
        ros2 service call /capture_frame std_srvs/srv/Trigger {}
        ;;
    start|continuous)
        echo "▶️  Starting continuous capture (1Hz)..."
        ros2 service call /capture_start_continuous std_srvs/srv/Trigger {}
        ;;
    stop)
        echo "⏹️  Stopping continuous capture..."
        ros2 service call /capture_stop_continuous std_srvs/srv/Trigger {}
        ;;
    status)
        echo "📡 Checking capture service status..."
        if ros2 service list | grep -q "capture_frame"; then
            echo "✅ Capture service is running"
            echo ""
            echo "Available services:"
            ros2 service list | grep capture | sed 's/^/  - /'
        else
            echo "❌ Capture service not found"
            echo "Start with: ros2 run capture_service capture_server"
        fi
        ;;
    help|*)
        echo "Capture CLI - On-demand frame capture"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  capture, single   Capture a single frame"
        echo "  start             Start 1Hz continuous capture"
        echo "  stop              Stop continuous capture"
        echo "  status            Check service availability"
        echo "  help              Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 capture              # Save one frame"
        echo "  $0 start                # Save frames every second"
        echo "  $0 stop                 # Stop saving"
        echo ""
        echo "Files saved to: captures/"
        ;;
esac