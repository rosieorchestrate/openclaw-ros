#!/usr/bin/env python3
"""
ROS2 Capture Client - CLI tool for triggering capture service.
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import sys


class CaptureClient(Node):
    """Simple client to trigger frame capture."""

    def __init__(self):
        super().__init__('capture_client')

    def call_service(self, service_name):
        """Call a trigger service and wait for response."""
        client = self.create_client(Trigger, service_name)
        
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(f'Service {service_name} not available')
            return False
        
        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'✅ {response.message}')
            else:
                self.get_logger().warning(f'⚠️  {response.message}')
            return response.success
        else:
            self.get_logger().error('Service call failed')
            return False


def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) < 2:
        print("Usage: ros2 run capture_service capture_client <command>")
        print("")
        print("Commands:")
        print("  capture     - Capture single frame")
        print("  start       - Start continuous capture (1Hz)")
        print("  stop        - Stop continuous capture")
        print("")
        print("Examples:")
        print("  ros2 run capture_service capture_client capture")
        print("  ros2 run capture_service capture_client start")
        print("  ros2 run capture_service capture_client stop")
        sys.exit(1)
    
    command = sys.argv[1]
    node = CaptureClient()
    
    service_map = {
        'capture': '/capture_frame',
        'start': '/capture_start_continuous',
        'stop': '/capture_stop_continuous'
    }
    
    if command not in service_map:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(service_map.keys())}")
        sys.exit(1)
    
    success = node.call_service(service_map[command])
    
    node.destroy_node()
    rclpy.shutdown()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()