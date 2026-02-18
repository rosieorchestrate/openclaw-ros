"""
Launch file for the surveillance system.
Launches camera_ros, detector_node, and notification_node.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments
    camera_arg = DeclareLaunchArgument(
        'camera',
        default_value='0',
        description='Camera ID or name'
    )
    
    width_arg = DeclareLaunchArgument(
        'width',
        default_value='640',
        description='Image width'
    )
    
    height_arg = DeclareLaunchArgument(
        'height',
        default_value='480',
        description='Image height'
    )
    
    confidence_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.5',
        description='Detection confidence threshold'
    )
    
    rate_arg = DeclareLaunchArgument(
        'detection_rate',
        default_value='1.0',
        description='Detection frequency in Hz'
    )
    
    recipient_arg = DeclareLaunchArgument(
        'recipient_email',
        default_value='rosie.orchestrate@gmail.com',
        description='Email recipient for notifications'
    )
    
    captures_dir_arg = DeclareLaunchArgument(
        'captures_dir',
        default_value='./captures',
        description='Directory for captured detection images'
    )
    
    log_dir_arg = DeclareLaunchArgument(
        'log_dir',
        default_value='./logs',
        description='Directory for logs'
    )
    
    # Camera node (from camera_ros package)
    camera_node = Node(
        package='camera_ros',
        executable='camera_node',
        name='camera',
        parameters=[{
            'camera': LaunchConfiguration('camera'),
            'width': LaunchConfiguration('width'),
            'height': LaunchConfiguration('height'),
        }],
        output='screen',
    )
    
    # Person detector node
    detector_node = Node(
        package='surveillance_ros',
        executable='detector_node',
        name='person_detector',
        parameters=[{
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'detection_rate': LaunchConfiguration('detection_rate'),
            'save_detections': True,
            'captures_dir': LaunchConfiguration('captures_dir'),
            'image_topic': '/camera/image_raw',
        }],
        output='screen',
    )
    
    # Notification node
    notification_node = Node(
        package='surveillance_ros',
        executable='notification_node',
        name='notification',
        parameters=[{
            'recipient_email': LaunchConfiguration('recipient_email'),
            'sender_email': 'surveillance@localhost',
            'log_dir': LaunchConfiguration('log_dir'),
            'cooldown_seconds': 10.0,
        }],
        output='screen',
    )
    
    return LaunchDescription([
        # Arguments
        camera_arg,
        width_arg,
        height_arg,
        confidence_arg,
        rate_arg,
        recipient_arg,
        captures_dir_arg,
        log_dir_arg,
        # Nodes
        camera_node,
        detector_node,
        notification_node,
    ])