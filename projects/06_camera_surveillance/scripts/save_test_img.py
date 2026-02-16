import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

class ImageSaver(Node):
    def __init__(self):
        super().__init__('image_saver')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.listener_callback,
            10)
        self.image_received = False
        self.get_logger().info('Waiting for one image on /camera/image_raw...')

    def listener_callback(self, msg):
        if not self.image_received:
            try:
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                save_path = '/home/opencw/.openclaw/workspace/camera_test.jpg'
                cv2.imwrite(save_path, cv_image)
                self.get_logger().info(f'Image saved to {save_path}')
                self.image_received = True
            except Exception as e:
                self.get_logger().error(f'Failed to save image: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = ImageSaver()
    # Spin until one image is saved or timeout
    start_time = rclpy.clock.Clock().now()
    while rclpy.ok() and not node.image_received:
        rclpy.spin_once(node, timeout_sec=0.1)
        if (rclpy.clock.Clock().now() - start_time).nanoseconds > 5e9: # 5 second timeout
            node.get_logger().error('Timeout waiting for image')
            break
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
