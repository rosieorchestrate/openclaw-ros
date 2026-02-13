import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random
import time

class RandomTalker(Node):
    def __init__(self):
        super().__init__('random_talker')
        self.publisher_ = self.create_publisher(String, '/turtle_chatter', 10)
        
        # ROS2 Observability: Log startup and parameters
        self.get_logger().info('node=random_talker event=startup status=ok')
        
        # Schedule the first random message
        self.schedule_next()

    def schedule_next(self):
        delay = random.uniform(0.5, 3.0)
        self.timer = self.create_timer(delay, self.timer_callback)

    def timer_callback(self):
        # Cancel current one-shot timer to create next random interval
        self.timer.cancel()
        
        msg = String()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        msg.data = f'hello [{timestamp}]'
        
        self.publisher_.publish(msg)
        # Observability Contract: Structured log
        self.get_logger().info(f'event=message_published data="{msg.data}"')
        
        self.schedule_next()

def main(args=None):
    rclpy.init(args=args)
    node = RandomTalker()
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().fatal(f'event=critical_failure error="{e}"')
    finally:
        # Development Contract: Graceful exit
        node.get_logger().info('event=shutdown status=ok')
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
