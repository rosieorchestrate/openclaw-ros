from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Existing camera_ros package node
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera',
            parameters=[{'width': 640, 'height': 480}]
        ),
        # Detector Node
        Node(
            package='surveillance_system',
            executable='detector_node',
            name='detector',
            parameters=[{'detection_interval': 1.0}]
        ),
        # Mock Notifier Node
        Node(
            package='surveillance_system',
            executable='mock_notifier',
            name='notifier'
        )
    ])
