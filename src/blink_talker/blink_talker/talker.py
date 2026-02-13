import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random
import time

class RandomTalker(Node):
    def __init__(self):
        super().__init__('random_talker')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.get_logger().info('Random Talker started.')
        self.schedule_next_message()

    def schedule_next_message(self):
        # Random delay between 0.5 and 3.0 seconds
        delay = random.uniform(0.5, 3.0)
        self.timer = self.create_timer(delay, self.timer_callback)

    def timer_callback(self):
        # Cancel current timer to reschedule with a new random period
        self.timer.cancel()
        
        msg = String()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        msg.data = f'hello [{timestamp}]'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        
        self.schedule_next_message()

def main(args=None):
    rclpy.init(args=args)
    talker = RandomTalker()
    try:
        rclpy.spin(talker)
    except Exception as e:
        talker.get_logger().fatal(f'Talker failed: {e}')
    finally:
        talker.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
