from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtle_talker',
            executable='talker',
            name='random_talker',
            output='screen'
        ),
        Node(
            package='turtle_talker',
            executable='listener',
            name='terminal_listener',
            output='screen'
        ),
        # Turtlesim as visual proxy for Level 1 Sim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim_turtlesim',
            output='screen'
        ),
    ])
