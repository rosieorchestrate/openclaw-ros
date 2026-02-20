#!/bin/bash
# Status monitor for surveillance system

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Surveillance System Status          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Check if ROS2 nodes are running
echo "📡 ROS2 Nodes:"
if pgrep -f "camera_node" > /dev/null; then
    echo -e "  ${GREEN}●${NC} Camera Node: RUNNING"
else
    echo -e "  ${RED}○${NC} Camera Node: STOPPED"
fi

if pgrep -f "detector_node" > /dev/null; then
    echo -e "  ${GREEN}●${NC} Detector Node: RUNNING"
else
    echo -e "  ${RED}○${NC} Detector Node: STOPPED"
fi

if pgrep -f "email_node" > /dev/null; then
    echo -e "  ${GREEN}●${NC} Email Node: RUNNING"
else
    echo -e "  ${RED}○${NC} Email Node: STOPPED"
fi

echo ""

# Directory stats
echo "📁 Storage:"
echo "  Captures: $(ls -1 "$PROJECT_DIR/captures"/*.jpg 2>/dev/null | wc -l) files"
echo "  Logs: $(ls -1 "$PROJECT_DIR/logs"/*.log 2>/dev/null | wc -l) files"

if [ -f "$PROJECT_DIR/logs/mock_emails.log" ]; then
    echo "  Alerts sent: $(grep -c "MOCK EMAIL" "$PROJECT_DIR/logs/mock_emails.log" 2>/dev/null || echo 0)"
fi

echo ""

# Recent captures
echo "📷 Recent Captures:"
ls -lt "$PROJECT_DIR/captures"/*.jpg 2>/dev/null | head -3 | awk '{print "  " $9}' | sed 's|.*/||' || echo "  (none yet)"

echo ""

# System temp (if available)
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(( $(cat /sys/class/thermal/thermal_zone0/temp) / 1000 ))
    if [ $TEMP -gt 75 ]; then
        echo -e "🌡️  CPU Temp: ${RED}${TEMP}°C (WARNING)${NC}"
    elif [ $TEMP -gt 60 ]; then
        echo -e "🌡️  CPU Temp: ${YELLOW}${TEMP}°C (warm)${NC}"
    else
        echo -e "🌡️  CPU Temp: ${GREEN}${TEMP}°C (normal)${NC}"
    fi
fi

echo ""
echo "Useful commands:"
echo "  View logs:    tail -f $PROJECT_DIR/logs/mock_emails.log"
echo "  List captures: ls -la $PROJECT_DIR/captures/"
echo "  Stop system:  pkill -f 'camera_surveillance'"
