from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    project_dir = "/home/opencw/.openclaw/openclaw-ros/projects/05_camera_surveillance"
    return LaunchDescription([
        Node(package='surveillance_logic', executable='surveillant', name='surveillant',
             parameters=[{'temp_image_dir': f'{project_dir}/logs/temp_captures'}]),
        Node(package='surveillance_logic', executable='email_mocker', name='email_mocker',
             parameters=[{'log_dir': f'{project_dir}/logs/emails'}]),
    ])
