import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
import cv2
from cv_bridge import CvBridge
import numpy as np

class VirtualCamera(Node):
    def __init__(self):
        super().__init__('virtual_camera')
        # Use sensor_data per ros2.generation.pro for high-bandwidth topics
        self.publisher_ = self.create_publisher(Image, '/camera/image_raw', qos_profile_sensor_data)
        self.bridge = CvBridge()
        
        # ROS2 Observability
        self.get_logger().info('node=virtual_camera event=startup status=ok level=2')
        
        self.timer = self.create_timer(0.1, self.timer_callback) # 10Hz

    def timer_callback(self):
        # Generate a synthetic test pattern (color bars)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, 0:213] = (255, 0, 0)    # Blue
        img[:, 213:426] = (0, 255, 0)  # Green
        img[:, 426:640] = (0, 0, 255)  # Red
        
        # Add a timestamp to verify live data
        cv2.putText(img, f"SIMULATION LEVEL 2 - {self.get_clock().now().to_msg().sec}", 
                    (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_link"
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VirtualCamera()
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().fatal(f'event=critical_failure error="{e}"')
    finally:
        node.get_logger().info('event=shutdown status=ok')
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
