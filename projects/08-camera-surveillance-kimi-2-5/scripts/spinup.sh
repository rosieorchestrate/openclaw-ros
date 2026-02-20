#!/bin/bash
# Spin-up procedure for Camera Surveillance System
# Run this to build, install and launch the surveillance system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Camera Surveillance System - Setup${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Detect project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$PROJECT_DIR/src"

echo "📁 Project directory: $PROJECT_DIR"

# Check ROS2
if [ -z "$ROS_DISTRO" ]; then
    echo -e "${YELLOW}⚠ ROS2 not sourced. Sourcing now...${NC}"
    if [ -f "/opt/ros/kilted/local_setup.bash" ]; then
        source /opt/ros/kilted/local_setup.bash
        echo -e "${GREEN}✓ Sourced ROS2 Kilted${NC}"
    else
        echo -e "${RED}❌ ROS2 not found at /opt/ros/kilted/${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ ROS2 already sourced: $ROS_DISTRO${NC}"
fi

# Ensure directories exist
echo ""
echo "📂 Ensuring directory structure..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/captures"
mkdir -p "$PROJECT_DIR/models"
mkdir -p "$PROJECT_DIR/install"

# Verify camera
echo ""
echo "📷 Verifying camera..."
if cam --list 2>/dev/null | grep -q "imx219"; then
    echo -e "${GREEN}✓ Camera detected: imx219${NC}"
else
    echo -e "${YELLOW}⚠ Camera not detected. Check connections.${NC}"
fi

# Build
echo ""
echo "🔨 Building workspace..."
cd "$PROJECT_DIR"

# Clean previous build if exists
if [ -d "build" ]; then
    echo "   Cleaning previous build..."
    rm -rf build install log
fi

colcon build --packages-select camera_surveillance --symlink-install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Source workspace
echo ""
echo "📥 Sourcing workspace..."
source "$PROJECT_DIR/install/local_setup.bash"
echo -e "${GREEN}✓ Workspace sourced${NC}"

# Check dependencies
echo ""
echo "🔍 Checking Python dependencies..."
python3 -c "import cv2; import numpy" 2>/dev/null && echo -e "${GREEN}✓ OpenCV & NumPy available${NC}" || echo -e "${YELLOW}⚠ Install: pip3 install opencv-python numpy${NC}"

# Summary
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Setup Complete! 🎉${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Quick camera test:"
echo "   $PROJECT_DIR/scripts/grab_frame.sh"
echo ""
echo "2️⃣  Launch surveillance (mock mode):"
echo "   cd $PROJECT_DIR"
echo "   source install/local_setup.bash"
echo "   ros2 launch camera_surveillance surveillance.launch.py"
echo ""
echo "3️⃣  View logs:"
echo "   tail -f $PROJECT_DIR/logs/mock_emails.log"
echo "   tail -f $PROJECT_DIR/logs/surveillance.log"
echo ""
echo "📁 Captures saved to: $PROJECT_DIR/captures/"
echo ""
