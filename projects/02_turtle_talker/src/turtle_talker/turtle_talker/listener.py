import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TerminalListener(Node):
    def __init__(self):
        super().__init__('terminal_listener')
        self.subscription = self.create_subscription(
            String,
            '/turtle_chatter',
            self.listener_callback,
            10)
        self.get_logger().info('node=terminal_listener event=startup status=ok')

    def listener_callback(self, msg):
        # Observability Contract: Structured log
        self.get_logger().info(f'event=message_received data="{msg.data}"')
        # Human-readable output requested by Noah/Jakub
        print(f'I heard: [{msg.data}]')

def main(args=None):
    rclpy.init(args=args)
    node = TerminalListener()
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
