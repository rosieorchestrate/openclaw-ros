import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
import os
import time

class DetectionLogger(Node):
    def __init__(self):
        super().__init__('detection_logger')
        
        self.declare_parameter('log_dir', 'logs')
        log_dir = self.get_parameter('log_dir').value
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(log_dir, exist_ok=True)

        # Unique log file for this run
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f'detections_{timestamp}.log')
        
        self.subscription = self.create_subscription(
            Detection2DArray, '/detections', self.listener_callback, 10)
        
        self.get_logger().info(f'node=detection_logger event=startup status=ok log_file={self.log_file}')

    def listener_callback(self, msg):
        detection_list = []
        for det in msg.detections:
            for result in det.results:
                detection_list.append((result.hypothesis.class_id, round(result.hypothesis.score, 2)))

        if not detection_list:
            return

        timestamp = f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec}"
        log_entry = f"timestamp: {timestamp}, objects: {detection_list}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        self.get_logger().info(f'event=detections_logged count={len(detection_list)}')

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
