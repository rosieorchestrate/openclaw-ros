from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from pathlib import Path


def generate_launch_description():
    """Generate launch description for camera surveillance system using camera_ros."""
    
    # Get project directory for log paths
    project_dir = Path(__file__).parent.parent.parent.parent
    
    # Launch arguments
    mock_mode_arg = DeclareLaunchArgument(
        'mock_mode',
        default_value='true',
        description='Enable mock email mode (logs to file instead of sending)'
    )
    
    confidence_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.5',
        description='Minimum confidence for person detection (0.0-1.0)'
    )
    
    camera_id_arg = DeclareLaunchArgument(
        'camera_id',
        default_value='0',
        description='Camera ID (0 for imx219 on Pi)'
    )
    
    email_to_arg = DeclareLaunchArgument(
        'email_to',
        default_value='rosie.orchestrate@gmail.com',
        description='Email recipient for alerts'
    )
    
    # camera_ros node (official libcamera ROS2 integration)
    camera_ros_node = Node(
        package='camera_ros',
        executable='camera_node',
        name='camera_ros',
        output='screen',
        parameters=[{
            'camera': LaunchConfiguration('camera_id'),
            'width': 640,
            'height': 480,
            'format': 'RGB888',
            'frame_rate': 1.0,  # 1 Hz to prevent overload
        }],
        remappings=[
            ('image_raw', '/camera/image_raw'),
            ('camera_info', '/camera/camera_info'),
        ]
    )
    
    # Person detection node
    detector_node = Node(
        package='camera_surveillance',
        executable='detector_node',
        name='detector_node',
        output='screen',
        parameters=[{
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'capture_dir': str(project_dir / 'captures'),
            'model_dir': str(project_dir / 'models')
        }]
    )
    
    # Email notification node
    email_node = Node(
        package='camera_surveillance',
        executable='email_node',
        name='email_node',
        output='screen',
        parameters=[{
            'mock_mode': LaunchConfiguration('mock_mode'),
            'email_to': LaunchConfiguration('email_to'),
            'email_from': 'surveillance@rosie.local',
            'log_directory': str(project_dir / 'logs'),
            'capture_directory': str(project_dir / 'captures')
        }]
    )
    
    return LaunchDescription([
        mock_mode_arg,
        confidence_arg,
        camera_id_arg,
        email_to_arg,
        camera_ros_node,
        detector_node,
        email_node
    ])
