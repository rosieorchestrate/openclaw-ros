#!/bin/bash
# Acceptance Test for Turtle Talker (Milestone 1)

PROJECT_ROOT="/home/opencw/.openclaw/openclaw-ros/projects/02_turtle_talker/src/turtle_talker"
source /opt/ros/kilted/setup.zsh
source $PROJECT_ROOT/install/setup.zsh

echo "Verifying ROS 2 Graph..."
# Check for nodes
NODES=$(ros2 node list)
[[ $NODES == *"/random_talker"* ]] || { echo "FAILURE: random_talker not found"; exit 1; }
[[ $NODES == *"/terminal_listener"* ]] || { echo "FAILURE: terminal_listener not found"; exit 1; }

echo "Verifying INTERFACES.md compliant topics..."
# Check for topic
TOPICS=$(ros2 topic list)
[[ $TOPICS == *"/turtle_chatter"* ]] || { echo "FAILURE: /turtle_chatter not found"; exit 1; }

echo "Verifying Observability: Message flow detected..."
# Verify hz > 0
HZ=$(ros2 topic hz /turtle_chatter --window 3 | grep "average rate:" | head -n 1)
if [[ -z "$HZ" ]]; then
    echo "FAILURE: No message flow on /turtle_chatter"
    exit 1
fi

echo "SUCCESS: Acceptance criteria met."
exit 0
