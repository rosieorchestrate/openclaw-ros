# surveillance_ros ROS2 package
"""
ROS2-based surveillance system with person detection and email notifications.

Nodes:
- detector_node: Subscribes to camera images, detects persons using MediaPipe
- notification_node: Subscribes to detection events, sends mock email notifications

Topics:
- /camera/image_raw [sensor_msgs/Image] - Camera images (from camera_ros)
- /detection/person [std_msgs/String] - Person detection events
"""

from .detector_node import PersonDetectorNode
from .notification_node import NotificationNode

__all__ = ['PersonDetectorNode', 'NotificationNode']