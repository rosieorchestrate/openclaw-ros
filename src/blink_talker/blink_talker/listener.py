import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from gpiozero import LED
import time
import os

class BlinkListener(Node):
    def __init__(self):
        super().__init__('blink_listener')
        
        # Parameters
        self.declare_parameter('led_pin', 16)
        self.declare_parameter('log_dir', 'logs')
        
        pin = self.get_parameter('led_pin').get_parameter_value().integer_value
        self.log_dir = self.get_parameter('log_dir').get_parameter_value().string_value
        
        # Ensure log directory exists
        if not os.path.isabs(self.log_dir):
            # Resolve relative to package root for this test
            self.log_dir = os.path.join(os.getcwd(), self.log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        
        try:
            self.led = LED(pin)
            self.get_logger().info(f'LED initialized on pin {pin}')
        except Exception as e:
            self.get_logger().error(f'Failed to init LED: {e}')
            self.led = None

        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.get_logger().info('Blink Listener started.')

    def listener_callback(self, msg):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] {msg.data}\n'
        
        # Log to file
        log_file_path = os.path.join(self.log_dir, 'messages.log')
        with open(log_file_path, 'a') as f:
            f.write(log_entry)
        
        self.get_logger().info(f'Received and logged: "{msg.data}"')

        # Blink LED
        if self.led:
            self.led.on()
            time.sleep(0.3) # Short sleep for blink is acceptable in callback for this simple case
            self.led.off()

def main(args=None):
    rclpy.init(args=args)
    listener = BlinkListener()
    try:
        rclpy.spin(listener)
    except Exception as e:
        listener.get_logger().fatal(f'Listener failed: {e}')
    finally:
        if listener.led:
            listener.led.close()
        listener.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
