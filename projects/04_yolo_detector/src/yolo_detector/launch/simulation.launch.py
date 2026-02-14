from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('yolo_detector')
    # Using relative paths for simplicity in testing
    return LaunchDescription([
        # Reuse Project 03 Virtual Camera if possible, or create local Level 2 source
        Node(
            package='camera_capture',
            executable='virtual_camera',
            name='sim_camera',
            output='screen'
        ),
        Node(
            package='yolo_detector',
            executable='detector',
            name='yolo_node',
            output='screen',
            parameters=[{
                'model_path': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/config/models/yolo.weights',
                'config_path': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/config/models/yolo.cfg',
                'classes_path': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/config/models/coco.names',
                'confidence_threshold': 0.2
            }]
        ),
        Node(
            package='yolo_detector',
            executable='logger',
            name='detection_logger',
            output='screen',
            parameters=[{'log_dir': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/logs'}]
        ),
    ])
