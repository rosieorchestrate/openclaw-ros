#!/usr/bin/env python3
"""
ROS2 Launch file for the Camera Surveillance System.

Launches:
  1. camera_ros camera_node (libcamera → /camera/image_raw)
  2. camera_capture_node.py (throttle to 1fps)
  3. person_detector_node.py (MobileNet-SSD detection)
  4. alert_node.py (mock email alerts → logs/)

Usage:
  cd 07-camera-surveillance-opus-4-6
  source /opt/ros/kilted/setup.bash
  ros2 launch launch/surveillance_launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    # Project root — resolved at launch time
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nodes_dir = os.path.join(project_root, 'nodes')

    prototxt_path = os.path.join(project_root, 'models', 'deploy.prototxt')
    caffemodel_path = os.path.join(project_root, 'models', 'mobilenet_ssd.caffemodel')

    return LaunchDescription([
        LogInfo(msg=f'🎥 Surveillance System starting from: {project_root}'),

        # --- 1. Camera Node (libcamera → /camera/image_raw) ---
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera',
            output='screen',
            parameters=[{
                'width': 640,
                'height': 480,
                'camera': 0,
            }],
        ),

        # --- 2. Camera Capture Node (throttle to 1fps) ---
        # Small delay to let camera start publishing
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'python3', os.path.join(nodes_dir, 'camera_capture_node.py'),
                        '--ros-args',
                        '-p', 'input_topic:=/camera/image_raw',
                        '-p', 'output_topic:=/surveillance/throttled_image',
                        '-p', 'target_fps:=1.0',
                    ],
                    name='camera_capture_node',
                    output='screen',
                ),
            ],
        ),

        # --- 3. Person Detector Node ---
        TimerAction(
            period=5.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'python3', os.path.join(nodes_dir, 'person_detector_node.py'),
                        '--ros-args',
                        '-p', f'prototxt_path:={prototxt_path}',
                        '-p', f'caffemodel_path:={caffemodel_path}',
                        '-p', 'confidence_threshold:=0.5',
                        '-p', 'person_class_id:=15',
                        '-p', 'input_size:=300',
                        '-p', f'project_root:={project_root}',
                    ],
                    name='person_detector_node',
                    output='screen',
                ),
            ],
        ),

        # --- 4. Alert Node (mock email) ---
        TimerAction(
            period=5.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'python3', os.path.join(nodes_dir, 'alert_node.py'),
                        '--ros-args',
                        '-p', 'mock_mode:=true',
                        '-p', 'recipient:=rosie.orchestrate@gmail.com',
                        '-p', 'cooldown_seconds:=30.0',
                        '-p', f'project_root:={project_root}',
                    ],
                    name='alert_node',
                    output='screen',
                ),
            ],
        ),
    ])
