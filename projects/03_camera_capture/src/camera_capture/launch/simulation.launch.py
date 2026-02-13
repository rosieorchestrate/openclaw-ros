from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='camera_capture',
            executable='virtual_camera',
            name='virtual_camera',
            output='screen'
        ),
        Node(
            package='camera_capture',
            executable='image_saver',
            name='image_saver',
            output='screen',
            parameters=[{'output_dir': 'captures'}]
        ),
    ])
