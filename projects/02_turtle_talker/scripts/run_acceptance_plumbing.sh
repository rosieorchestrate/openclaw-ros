#!/bin/bash
# Acceptance Test for Turtle Talker (Milestone 1)

PROJECT_ROOT="/home/opencw/.openclaw/openclaw-ros/projects/02_turtle_talker/src/turtle_talker"
source /opt/ros/kilted/setup.sh
source $PROJECT_ROOT/install/setup.sh

echo "Verifying ROS 2 Graph..."
# Check for nodes reaching across Xvfb session
NODES=$(ros2 node list)
echo "Active nodes: $NODES"
[[ $NODES == *"/random_talker"* ]] || { echo "FAILURE: random_talker not found"; exit 1; }
[[ $NODES == *"/terminal_listener"* ]] || { echo "FAILURE: terminal_listener not found"; exit 1; }

echo "Verifying INTERFACES.md compliant topics..."
TOPICS=$(ros2 topic list)
echo "Active topics: $TOPICS"
[[ $TOPICS == *"/turtle_chatter"* ]] || { echo "FAILURE: /turtle_chatter not found"; exit 1; }

echo "Verifying Observability: Message flow detected..."
HZ=$(ros2 topic hz /turtle_chatter --window 3 | grep "average rate:" | head -n 1)
if [[ -z "$HZ" ]]; then
    echo "FAILURE: No message flow on /turtle_chatter"
    exit 1
fi
echo "Flow frequency: $HZ"

echo "SUCCESS: Acceptance criteria met."
exit 0
