from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    project_dir = "/home/opencw/.openclaw/openclaw-ros/projects/05_camera_surveillance"
    return LaunchDescription([
        # 1. Physical Camera (assuming hardware integration requested)
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera',
            output='screen'
        ),
        # 2. YOLO Detector (from P04)
        Node(
            package='yolo_detector',
            executable='detector',
            name='yolo_node',
            output='screen',
            parameters=[{
                'model_path': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/config/models/yolo.weights',
                'config_path': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/config/models/yolo.cfg',
                'classes_path': '/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector/config/models/coco.names',
                'confidence_threshold': 0.3
            }]
        ),
        # 3. Surveillant Logic
        Node(
            package='surveillance_logic',
            executable='surveillant',
            name='surveillant',
            output='screen',
            parameters=[{'temp_image_dir': f'{project_dir}/logs/temp_captures'}]
        ),
        # 4. Email Mocker
        Node(
            package='surveillance_logic',
            executable='email_mocker',
            name='email_mocker',
            output='screen',
            parameters=[{'log_dir': f'{project_dir}/logs/emails'}]
        ),
    ])
