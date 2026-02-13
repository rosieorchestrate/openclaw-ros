import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Empty
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import os
import time

class ImageSaver(Node):
    def __init__(self):
        super().__init__('image_saver')
        self.bridge = CvBridge()
        self.last_img = None
        
        # Ensure capture directory exists
        self.declare_parameter('output_dir', 'captures')
        self.output_dir = self.get_parameter('output_dir').get_parameter_value().string_value
        if not os.path.isabs(self.output_dir):
            self.output_dir = os.path.join(os.getcwd(), self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

        # Image Subscriber (Sensor Data QoS for parity with camera_ros)
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, qos_profile_sensor_data)
        
        # Trigger Subscriber
        self.trigger_sub = self.create_subscription(
            Empty, '/capture_request', self.trigger_callback, 10)

        self.get_logger().info(f'node=image_saver event=startup status=ok output_dir={self.output_dir}')

    def image_callback(self, msg):
        self.last_img = msg

    def trigger_callback(self, msg):
        if self.last_img is None:
            self.get_logger().warn('event=capture_failed reason="no image received yet"')
            return

        try:
            cv_img = self.bridge.imgmsg_to_cv2(self.last_img, desired_encoding="bgr8")
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f'capture_{timestamp}.jpg')
            
            cv2.imwrite(filename, cv_img)
            self.get_logger().info(f'event=image_saved path="{filename}"')
        except Exception as e:
            self.get_logger().error(f'event=capture_error error="{e}"')

def main(args=None):
    rclpy.init(args=args)
    node = ImageSaver()
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
