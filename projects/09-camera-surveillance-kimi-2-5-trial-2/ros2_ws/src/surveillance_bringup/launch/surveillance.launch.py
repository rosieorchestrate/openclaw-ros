from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch file for ROS2 Camera Surveillance System.
    Starts: camera_ros, capture_service, detection_node, email_node
    """
    
    # Declare arguments
    camera_width_arg = DeclareLaunchArgument(
        'camera_width',
        default_value='640',
        description='Camera capture width'
    )
    
    camera_height_arg = DeclareLaunchArgument(
        'camera_height',
        default_value='480',
        description='Camera capture height'
    )
    
    detection_rate_arg = DeclareLaunchArgument(
        'detection_rate',
        default_value='1.0',
        description='Detection frequency in Hz (default: 1Hz)'
    )
    
    target_email_arg = DeclareLaunchArgument(
        'target_email',
        default_value='rosie.orchestrate@gmail.com',
        description='Target email for notifications'
    )
    
    enable_capture_arg = DeclareLaunchArgument(
        'enable_capture',
        default_value='true',
        description='Enable capture service for on-demand frame capture'
    )

    # Camera node (camera_ros from apt)
    camera_node = Node(
        package='camera_ros',
        executable='camera_node',
        name='camera_node',
        output='screen',
        parameters=[{
            'width': LaunchConfiguration('camera_width'),
            'height': LaunchConfiguration('camera_height'),
            'format': 'RGB888',
            'camera': 0,
        }],
        remappings=[
            ('/camera/image_raw', '/camera/image_raw'),
        ]
    )

    # Capture service node
    capture_server_node = Node(
        package='capture_service',
        executable='capture_server',
        name='capture_server',
        output='screen',
        parameters=[{
            'input_topic': '/camera/image_raw',
            'output_dir': '../../captures',
            'continuous_rate': 1.0,
        }]
    )

    # Detection node
    detection_node = Node(
        package='detection_node',
        executable='detection_node',
        name='detection_node',
        output='screen',
        parameters=[{
            'detection_rate_hz': LaunchConfiguration('detection_rate'),
            'confidence_threshold': 0.5,
            'capture_dir': '../../captures',
            'model_dir': './models',
            'input_topic': '/camera/image_raw',
        }]
    )

    # Email node
    email_node = Node(
        package='email_node',
        executable='email_node',
        name='email_node',
        output='screen',
        parameters=[{
            'target_email': LaunchConfiguration('target_email'),
            'log_dir': '../../logs',
            'log_to_file': True,
            'input_topic': '/detection/events',
        }]
    )

    return LaunchDescription([
        camera_width_arg,
        camera_height_arg,
        detection_rate_arg,
        target_email_arg,
        enable_capture_arg,
        camera_node,
        capture_server_node,
        detection_node,
        email_node,
    ])