import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import time

class DetectionLogger(Node):
    def __init__(self):
        super().__init__('detection_logger')
        self.bridge = CvBridge()
        
        self.declare_parameter('log_dir', 'logs')
        self.declare_parameter('save_debug_images', False) # New Flag
        
        self.log_dir = self.get_parameter('log_dir').value
        self.debug_mode = self.get_parameter('save_debug_images').value
        
        if not os.path.isabs(self.log_dir):
            self.log_dir = os.path.join(os.getcwd(), self.log_dir)
        
        # Setup pathing based on mode
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        if self.debug_mode:
            self.run_dir = os.path.join(self.log_dir, f'debug_{timestamp}')
            os.makedirs(self.run_dir, exist_ok=True)
            self.log_file = os.path.join(self.run_dir, 'detections.log')
        else:
            os.makedirs(self.log_dir, exist_ok=True)
            self.log_file = os.path.join(self.log_dir, f'detections_{timestamp}.log')
            self.run_dir = None

        self.subscription = self.create_subscription(
            Detection2DArray, '/detections', self.det_callback, 10)
        
        # Optional Image Subscription
        self.img_sub = None
        if self.debug_mode:
            self.img_sub = self.create_subscription(
                Image, '/detections/visual_debug', self.img_callback, 10)
        
        self.last_detections = []
        self.get_logger().info(f'node=detection_logger event=startup status=ok debug={self.debug_mode}')

    def det_callback(self, msg):
        detection_list = []
        for det in msg.detections:
            for result in det.results:
                detection_list.append((result.hypothesis.class_id, round(result.hypothesis.score, 2)))

        self.last_detections = detection_list
        
        # Log data-only entry if not in debug mode
        if not self.debug_mode and detection_list:
            timestamp = f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec}"
            log_entry = f"timestamp: {timestamp}, objects: {detection_list}\n"
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            self.get_logger().info(f'event=detections_logged count={len(detection_list)}')

    def img_callback(self, msg):
        # Only called if debug_mode is True and image received
        timestamp = f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec}"
        img_path = os.path.join(self.run_dir, f"frame_{timestamp}.jpg")
        
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            cv2.imwrite(img_path, cv_img)
            
            log_entry = f"timestamp: {timestamp}, objects: {self.last_detections}, image: {img_path}\n"
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
                
            self.get_logger().info(f'event=detections_logged image=saved count={len(self.last_detections)}')
        except Exception as e:
            self.get_logger().error(f'event=log_error error="{e}"')

def main(args=None):
    rclpy.init(args=args)
    node = DetectionLogger()
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().fatal(f'event=critical_failure error="{e}"')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
