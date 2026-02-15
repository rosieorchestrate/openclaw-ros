from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    p_dir = "/home/opencw/.openclaw/openclaw-ros/projects/05_surveillance_pro"
    return LaunchDescription([
        Node(package='surveillance_logic', executable='surveillant', name='surveillant',
             parameters=[{'temp_image_dir': f'{p_dir}/logs/temp_captures'}]),
        Node(package='surveillance_logic', executable='email_mocker', name='email_mocker',
             parameters=[{'log_dir': f'{p_dir}/logs/emails'}]),
    ])
