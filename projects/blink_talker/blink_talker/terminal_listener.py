import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TerminalListener(Node):
    def __init__(self):
        super().__init__('terminal_listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.get_logger().info('Terminal Listener started. Monitoring /chatter...')

    def listener_callback(self, msg):
        # Similar to ROS2 demo listener: simple terminal output
        print(f'I heard: [{msg.data}]')

def main(args=None):
    rclpy.init(args=args)
    node = TerminalListener()
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().fatal(f'Terminal Listener failed: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
