import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from std_srvs.srv import Trigger
from cv_bridge import CvBridge
import cv2
import mediapipe as mp
import os
import time

class DetectorNode(Node):
    def __init__(self):
        super().__init__('detector_node')
        
        self.declare_parameter('detection_interval', 1.0) # 1Hz
        self.declare_parameter('capture_dir', '/home/opencw/.openclaw/openclaw-ros/projects/06_camera_surveillance/captures')
        
        self.interval = self.get_parameter('detection_interval').get_parameter_value().double_value
        self.capture_dir = self.get_parameter('capture_dir').get_parameter_value().string_value
        
        if not os.path.isabs(self.capture_dir):
            self.capture_dir = os.path.join(os.getcwd(), self.capture_dir)
        os.makedirs(self.capture_dir, exist_ok=True)

        self.bridge = CvBridge()
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.listener_callback,
            10)
        
        self.publisher_ = self.create_publisher(String, 'detections', 10)
        
        # Service for manual test capture
        self.srv = self.create_service(Trigger, 'save_test_frame', self.save_test_frame_callback)
        self.test_frame_requested = False
        
        self.last_detection_time = 0
        self.get_logger().info(f'Detector Node started (MediaPipe). Limit: {self.interval}s per check.')

    def save_test_frame_callback(self, request, response):
        self.test_frame_requested = True
        response.success = True
        response.message = "Test frame capture requested. It will be saved upon the next incoming image."
        return response

    def listener_callback(self, msg):
        current_time = time.time()
        
        try:
            # Convert ROS Image to OpenCV once per callback
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Handle manual test frame request (unfiltered by rate limit)
            if self.test_frame_requested:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'test_{timestamp}.jpg'
                save_path = os.path.join(self.capture_dir, filename)
                cv2.imwrite(save_path, cv_image)
                self.get_logger().info(f'Test frame saved to {save_path}')
                self.test_frame_requested = False

            # Rate limit for detection processing
            if current_time - self.last_detection_time < self.interval:
                return

            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
            # Inference on the CURRENT frame object
            results = self.pose.process(rgb_image)
            
            if results.pose_landmarks:
                self.last_detection_time = current_time
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'person_{timestamp}.jpg'
                save_path = os.path.join(self.capture_dir, filename)
                
                # Draw landmarks directly on the frame we just analyzed
                mp.solutions.drawing_utils.draw_landmarks(
                    cv_image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                
                # Save the analyzed/annotated frame
                cv2.imwrite(save_path, cv_image)
                
                # Notify
                detect_msg = String()
                detect_msg.data = f'Person detected! Frame saved to {save_path}'
                self.publisher_.publish(detect_msg)
                self.get_logger().warn(detect_msg.data)
                
        except Exception as e:
            self.get_logger().error(f'Detection failed: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
