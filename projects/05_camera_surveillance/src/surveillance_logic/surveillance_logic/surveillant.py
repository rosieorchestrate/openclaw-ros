import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import os
import time

class Surveillant(Node):
    def __init__(self):
        super().__init__('surveillant')
        self.bridge = CvBridge()
        self.latest_image = None
        self.last_process_time = 0.0
        
        self.declare_parameter('alert_target', 'rosie.orchestrate@gmail.com')
        self.declare_parameter('temp_image_dir', 'logs/temp_captures')
        
        self.target = self.get_parameter('alert_target').value
        self.temp_dir = self.get_parameter('temp_image_dir').value
        if not os.path.isabs(self.temp_dir):
            self.temp_dir = os.path.abspath(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Subscriptions
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.det_sub = self.create_subscription(Detection2DArray, '/detections', self.detection_callback, 10)
        
        # Publisher for alert
        self.alert_pub = self.create_publisher(String, '/surveillance/alert', 10)

        self.get_logger().info(f'node=surveillant event=startup status=ok target={self.target}')

    def image_callback(self, msg):
        self.latest_image = msg

    def detection_callback(self, msg):
        # Enforce 1Hz sampling logic
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self.last_process_time < 0.95:
            return
        
        people_found = []
        for det in msg.detections:
            for result in det.results:
                if result.hypothesis.class_id == 'person':
                    people_found.append(result.hypothesis.score)

        if people_found and self.latest_image:
            self.last_process_time = now
            self.trigger_alert(people_found)

    def trigger_alert(self, scores):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(self.latest_image, desired_encoding="bgr8")
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            img_name = f"person_{timestamp}.jpg"
            img_path = os.path.join(self.temp_dir, img_name)
            cv2.imwrite(img_path, cv_img)

            alert_msg = String()
            alert_msg.data = f"TARGET:{self.target}|SCORE:{max(scores):.2f}|PATH:{img_path}"
            
            self.alert_pub.publish(alert_msg)
            self.get_logger().info(f'event=person_detected score={max(scores):.2f} img={img_path}')
            
        except Exception as e:
            self.get_logger().error(f'event=alert_failure error="{e}"')

def main(args=None):
    rclpy.init(args=args)
    node = Surveillant()
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
