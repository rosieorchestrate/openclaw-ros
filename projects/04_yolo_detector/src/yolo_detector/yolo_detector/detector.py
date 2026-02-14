import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import os
import numpy as np

class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        self.bridge = CvBridge()
        self.latest_msg = None
        
        # Parameters
        self.declare_parameter('model_path', 'config/models/yolo.weights')
        self.declare_parameter('config_path', 'config/models/yolo.cfg')
        self.declare_parameter('classes_path', 'config/models/coco.names')
        self.declare_parameter('confidence_threshold', 0.5)
        
        # Load YOLO
        weights = self.get_parameter('model_path').value
        config = self.get_parameter('config_path').value
        classes = self.get_parameter('classes_path').value
        
        self.net = cv2.dnn.readNet(weights, config)
        with open(classes, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        # Publishers / Subscribers
        # Simulation Level 2: Strict parity with physical best-effort camera
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, qos_profile_sensor_data)
        self.publisher = self.create_publisher(Detection2DArray, '/detections', 10)

        # 1Hz Timer for Inference (Process one frame per second as per guidelines)
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info('node=yolo_detector event=startup status=ok model=yolov4-tiny rate=1Hz')

    def image_callback(self, msg):
        self.latest_msg = msg

    def timer_callback(self):
        if self.latest_msg is None:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_msg, desired_encoding='bgr8')
            height, width, _ = cv_image.shape

            # Inference
            blob = cv2.dnn.blobFromImage(cv_image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

            # Parse results
            detections = Detection2DArray()
            detections.header = self.latest_msg.header
            
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > self.get_parameter('confidence_threshold').value:
                        det = Detection2D()
                        hyp = ObjectHypothesisWithPose()
                        hyp.hypothesis.class_id = self.classes[class_id]
                        hyp.hypothesis.score = float(confidence)
                        det.results.append(hyp)
                        detections.detections.append(det)

            self.publisher.publish(detections)
            self.get_logger().info(f'event=inference_complete detections={len(detections.detections)}')

        except Exception as e:
            self.get_logger().error(f'event=inference_failure error="{e}"')

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().fatal(f'event=critical_failure error="{e}"')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
