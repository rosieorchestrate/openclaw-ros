#!/bin/bash
# verify_complete_flow.sh - Verify all components are present and configured

echo "========================================="
echo "COMPLETE FLOW VERIFICATION"
echo "========================================="
echo ""

PROJECT_DIR="$HOME/.openclaw/openclaw-ros/09-camera-surveillance-kimi-2-5-trial-2"

check_file() {
    if [ -f "$1" ]; then
        echo "  ✅ $2"
        return 0
    else
        echo "  ❌ $2 (missing: $1)"
        return 1
    fi
}

echo "1. PACKAGE STRUCTURE"
echo "--------------------"
ALL_PRESENT=0

# Core packages
check_file "$PROJECT_DIR/ros2_ws/src/camera_node/package.xml" "camera_node package" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/detection_node/package.xml" "detection_node package" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/email_node/package.xml" "email_node package" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/capture_service/package.xml" "capture_service package" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/surveillance_bringup/package.xml" "surveillance_bringup package" || ALL_PRESENT=1

echo ""
echo "2. DETECTION NODE (1Hz person detection)"
echo "-----------------------------------------"
check_file "$PROJECT_DIR/ros2_ws/src/detection_node/detection_node/detection_node.py" "Detection implementation" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/detection_node/setup.py" "Detection setup.py" || ALL_PRESENT=1

echo ""
echo "3. EMAIL NODE (Mock email + logging)"
echo "-------------------------------------"
check_file "$PROJECT_DIR/ros2_ws/src/email_node/email_node/email_node.py" "Email implementation" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/email_node/setup.py" "Email setup.py" || ALL_PRESENT=1

echo "   Features:"
echo "     • Terminal output with 🚨 alert banner"
echo "     • File logging to logs/mock_emails_*.log"
echo "     • References detection frame with bounding boxes"
echo "     • Target: rosie.orchestrate@gmail.com"

echo ""
echo "4. CAPTURE SERVICE (On-demand)"
echo "-------------------------------"
check_file "$PROJECT_DIR/ros2_ws/src/capture_service/capture_service/capture_server.py" "Capture server" || ALL_PRESENT=1
check_file "$PROJECT_DIR/ros2_ws/src/capture_service/capture_service/capture_client.py" "Capture client" || ALL_PRESENT=1

echo "   Services:"
echo "     • /capture_frame - Single frame capture"
echo "     • /capture_start_continuous - 1Hz continuous"
echo "     • /capture_stop_continuous - Stop continuous"

echo ""
echo "5. LAUNCH INTEGRATION"
echo "---------------------"
check_file "$PROJECT_DIR/ros2_ws/src/surveillance_bringup/launch/surveillance.launch.py" "Main launch file" || ALL_PRESENT=1

echo "   Launch sequence:"
echo "     1. camera_ros (libcamera → /camera/image_raw)"
echo "     2. capture_server (on-demand capture services)"
echo "     3. detection_node (1Hz person detection)"
echo "     4. email_node (mock email notifications)"

echo ""
echo "6. UTILITIES"
echo "------------"
check_file "$PROJECT_DIR/scripts/build_workspace.sh" "Build script" || ALL_PRESENT=1
check_file "$PROJECT_DIR/scripts/capture_cli.sh" "Capture CLI" || ALL_PRESENT=1
check_file "$PROJECT_DIR/scripts/demo_flow.sh" "Flow demo script" || ALL_PRESENT=1
check_file "$PROJECT_DIR/scripts/test_flow.py" "Flow test (Python)" || ALL_PRESENT=1
check_file "$PROJECT_DIR/scripts/test_email_flow.sh" "Email flow test" || ALL_PRESENT=1

echo ""
echo "7. DATA FLOW VERIFICATION"
echo "-------------------------"
echo "  📷 Camera Feed:"
echo "     Source: camera_ros (apt package)"
echo "     Topic: /camera/image_raw"
echo "     Format: RGB888, 640x480"
echo ""
echo "  🔍 Detection (1Hz):"
echo "     Input: /camera/image_raw"
echo "     Model: MobileNet-SSD COCO (person class)"
echo "     Output: captures/detection_*.jpg (with bounding boxes)"
echo "     Event: /detection/events (JSON)"
echo ""
echo "  📧 Email (Mock):"
echo "     Input: /detection/events"
echo "     Terminal: 🚨 PERSON DETECTED banner"
echo "     File: logs/mock_emails_*.log"
echo "     Content: Detection data + frame reference"
echo ""
echo "  📸 Capture (On-demand):"
echo "     Input: /camera/image_raw"
echo "     Output: captures/capture_*.jpg"
echo "     Control: /capture_* services"

echo ""
echo "========================================="
if [ $ALL_PRESENT -eq 0 ]; then
    echo "✅ ALL COMPONENTS PRESENT"
    echo "========================================="
    echo ""
    echo "Ready to build and test:"
    echo "  ./scripts/build_workspace.sh"
    echo ""
    echo "Or test individual flows:"
    echo "  ./scripts/demo_flow.sh           # Full flow test"
    echo "  ./scripts/test_email_flow.sh     # Email only"
    exit 0
else
    echo "⚠️  SOME COMPONENTS MISSING"
    echo "========================================="
    exit 1
fi