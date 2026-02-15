import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os
import time

class EmailMocker(Node):
    def __init__(self):
        super().__init__('email_mocker')
        
        self.declare_parameter('log_dir', 'logs/emails')
        self.log_dir = self.get_parameter('log_dir').value
        if not os.path.isabs(self.log_dir):
            self.log_dir = os.path.abspath(self.log_dir)
        os.makedirs(self.log_dir, exist_ok=True)

        self.sub = self.create_subscription(String, '/surveillance/alert', self.alert_callback, 10)
        
        self.get_logger().info(f'node=email_mocker event=startup status=ok log_dir={self.log_dir}')

    def alert_callback(self, msg):
        try:
            parts = msg.data.split('|')
            target = parts[0].split(':')[1]
            score = parts[1].split(':')[1]
            path = parts[2].split(':')[1]

            # Terminal Monitoring
            self.get_logger().info(f'DETECTION HAPPENED: person conf={score}')
            print(f"\n[MOCK EMAIL SERVICE]\nTo: {target}\nSubject: SECURITY ALERT\nImage: {path}\n")

            # File Persistence
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(self.log_dir, f'email_{timestamp}.txt')
            with open(log_file, 'w') as f:
                f.write(f"To: {target}\nScore: {score}\nImage: {path}\n")
                
            self.get_logger().info(f'event=email_mocked path={log_file}')
            
        except Exception as e:
            self.get_logger().error(f'event=mock_failure error="{e}"')

def main(args=None):
    rclpy.init(args=args)
    node = EmailMocker()
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
