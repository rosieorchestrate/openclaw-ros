import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os
import time

class MockEmailNotifier(Node):
    def __init__(self):
        super().__init__('mock_email_notifier')
        
        self.declare_parameter('email_target', 'rosie.orchestrate@gmail.com')
        self.declare_parameter('log_dir', '/home/opencw/.openclaw/openclaw-ros/projects/06_camera_surveillance/logs')
        
        self.target = self.get_parameter('email_target').get_parameter_value().string_value
        self.log_dir = self.get_parameter('log_dir').get_parameter_value().string_value
        
        # Resolve log path
        if not os.path.isabs(self.log_dir):
            self.log_dir = os.path.join(os.getcwd(), self.log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, 'email_mocks.log')

        self.subscription = self.create_subscription(
            String,
            'detections',
            self.detection_callback,
            10)
        
        self.get_logger().info(f'Mock Email Notifier initialized. Target: {self.target}')
        self.get_logger().info(f'Logging to: {self.log_file}')

    def detection_callback(self, msg):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        content = f"--- MOCK EMAIL ---\nTo: {self.target}\nSubject: Person Detected!\nTime: {timestamp}\nDetails: {msg.data}\n------------------\n"
        
        # Log to terminal
        self.get_logger().warn(f'DETECTION: {msg.data}. Sending mock email to {self.target}')
        
        # Log to file
        with open(self.log_file, 'a') as f:
            f.write(content)

def main(args=None):
    rclpy.init(args=args)
    node = MockEmailNotifier()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
