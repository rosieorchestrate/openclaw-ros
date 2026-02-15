from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    project_dir = "/home/opencw/.openclaw/openclaw-ros/projects/05_camera_surveillance"
    yolo_dir = "/home/opencw/.openclaw/openclaw-ros/projects/04_yolo_detector"
    return LaunchDescription([
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera'
        ),
        Node(
            package='yolo_detector',
            executable='detector',
            name='yolo_node',
            parameters=[{
                'model_path': f'{yolo_dir}/config/models/yolo.weights',
                'config_path': f'{yolo_dir}/config/models/yolo.cfg',
                'classes_path': f'{yolo_dir}/config/models/coco.names',
                'confidence_threshold': 0.3
            }]
        ),
        Node(
            package='surveillance_logic',
            executable='surveillant',
            name='surveillant',
            parameters=[{'temp_image_dir': f'{project_dir}/logs/temp_captures'}]
        ),
        Node(
            package='surveillance_logic',
            executable='email_mocker',
            name='email_mocker',
            parameters=[{'log_dir': f'{project_dir}/logs/emails'}]
        ),
    ])
