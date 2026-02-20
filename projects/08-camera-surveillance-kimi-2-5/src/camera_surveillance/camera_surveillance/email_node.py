#!/usr/bin/env python3
"""
Email Alert Node (Mock Mode)

Receives detection events and either:
- MOCKS: Logs to terminal and writes to log file
- REAL MODE: Sends actual email with attachment

Configuration via parameters. Mock mode is default for safety.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import json
import os
from datetime import datetime
from pathlib import Path


class EmailNode(Node):
    """ROS2 Node for email notifications on detection events."""
    
    def __init__(self):
        super().__init__('email_node')
        
        # Parameters
        self.declare_parameter('mock_mode', True)  # Default to mock for safety
        self.declare_parameter('email_to', 'rosie.orchestrate@gmail.com')
        self.declare_parameter('email_from', 'surveillance@rosie.local')
        self.declare_parameter('smtp_server', 'smtp.gmail.com')
        self.declare_parameter('smtp_port', 587)
        self.declare_parameter('smtp_username', '')
        self.declare_parameter('smtp_password', '')
        self.declare_parameter('log_directory', '')
        self.declare_parameter('capture_directory', '')
        
        self.mock_mode = self.get_parameter('mock_mode').value
        self.email_to = self.get_parameter('email_to').value
        self.email_from = self.get_parameter('email_from').value
        
        # Determine log directory
        log_dir_param = self.get_parameter('log_directory').value
        if log_dir_param:
            self.log_dir = Path(log_dir_param)
        else:
            # Default to project logs directory
            project_root = Path(__file__).parent.parent.parent.parent.parent
            self.log_dir = project_root / 'logs'
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine capture directory
        capture_dir_param = self.get_parameter('capture_directory').value
        if capture_dir_param:
            self.capture_dir = Path(capture_dir_param)
        else:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            self.capture_dir = project_root / 'captures'
        
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file for mock emails
        self.mock_log_file = self.log_dir / 'mock_emails.log'
        
        # CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Latest frame buffer (for saving with alert)
        self.latest_frame = None
        
        # Subscribers
        self.detection_sub = self.create_subscription(
            String,
            'detection/events',
            self.detection_callback,
            10
        )
        
        self.image_sub = self.create_subscription(
            Image,
            'camera/image_raw',
            self.image_callback,
            1
        )
        
        # Alert throttling (prevent email spam)
        self.last_alert_time = None
        self.min_alert_interval_sec = 60  # Max 1 email per minute
        
        # Stats
        self.alerts_sent = 0
        self.alerts_throttled = 0
        
        self.get_logger().info('📧 Email Node initializing...')
        self.get_logger().info(f'   Mode: {"MOCK (console + log file)" if self.mock_mode else "REAL"}')
        self.get_logger().info(f'   Recipient: {self.email_to}')
        self.get_logger().info(f'   Log directory: {self.log_dir}')
        self.get_logger().info(f'   Capture directory: {self.capture_dir}')
        self.get_logger().info('✅ Email Node ready')
    
    def image_callback(self, msg: Image):
        """Buffer latest frame for detection alerts."""
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().warning(f'Failed to convert image: {e}')
    
    def detection_callback(self, msg: String):
        """Handle detection event."""
        try:
            detection = json.loads(msg.data)
            confidence = detection.get('confidence', 0)
            timestamp = detection.get('timestamp', datetime.now().isoformat())
            
            # Throttle alerts
            now = datetime.now()
            if self.last_alert_time:
                elapsed = (now - self.last_alert_time).total_seconds()
                if elapsed < self.min_alert_interval_sec:
                    self.alerts_throttled += 1
                    self.get_logger().debug(f'Alert throttled ({elapsed:.1f}s < {self.min_alert_interval_sec}s)')
                    return
            
            self.last_alert_time = now
            self.alerts_sent += 1
            
            if self.mock_mode:
                self._mock_send_email(detection)
            else:
                self._send_real_email(detection)
                
        except json.JSONDecodeError as e:
            self.get_logger().error(f'Invalid detection message: {e}')
        except Exception as e:
            self.get_logger().error(f'Error processing detection: {e}')
    
    def _mock_send_email(self, detection: dict):
        """Mock email sending - logs to terminal and file."""
        import cv2
        
        timestamp = detection.get('timestamp', datetime.now().isoformat())
        confidence = detection.get('confidence', 0)
        
        # Save detection image if available
        image_path = None
        if self.latest_frame is not None:
            try:
                filename = f"detection_{timestamp.replace(':', '-')}.jpg"
                image_path = self.capture_dir / filename
                cv2.imwrite(str(image_path), self.latest_frame)
                self.get_logger().info(f'   Frame saved: {image_path}')
            except Exception as e:
                self.get_logger().warning(f'Failed to save detection frame: {e}')
        
        # Build mock email content
        email_content = f"""
========================================
MOCK EMAIL NOTIFICATION
========================================
To: {self.email_to}
From: {self.email_from}
Subject: 🚨 Person Detected - Surveillance Alert
Time: {timestamp}
----------------------------------------
DETECTION DETAILS:
  - Confidence: {confidence:.2%}
  - Location: Camera Feed
  - Alert #: {self.alerts_sent}
----------------------------------------
ATTACHMENT:
  - {image_path if image_path else "No image available"}
----------------------------------------
[This is a mock email - no actual message sent]
========================================
"""
        
        # Log to terminal (prominent)
        self.get_logger().warning('╔════════════════════════════════════╗')
        self.get_logger().warning('║     🚨 PERSON DETECTED!            ║')
        self.get_logger().warning('╠════════════════════════════════════╣')
        self.get_logger().warning(f'║ Confidence: {confidence:.2%}                    ║')
        self.get_logger().warning(f'║ Time: {datetime.now().strftime("%H:%M:%S")}                    ║')
        self.get_logger().warning('║ [MOCK EMAIL - See logs for details]║')
        self.get_logger().warning('╚════════════════════════════════════╝')
        
        # Write to log file
        try:
            with open(self.mock_log_file, 'a') as f:
                f.write(email_content)
                f.write('\n')
            self.get_logger().info(f'📝 Mock email logged to: {self.mock_log_file}')
        except Exception as e:
            self.get_logger().error(f'Failed to write mock email log: {e}')
    
    def _send_real_email(self, detection: dict):
        """Send actual email (requires SMTP configuration)."""
        # This would be implemented for production use
        self.get_logger().warning('Real email mode not yet implemented. Use mock mode for testing.')
    
    def get_status(self) -> dict:
        """Return current node status."""
        return {
            'alerts_sent': self.alerts_sent,
            'alerts_throttled': self.alerts_throttled,
            'mock_mode': self.mock_mode,
            'log_file': str(self.mock_log_file)
        }


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = EmailNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals():
            status = node.get_status()
            node.get_logger().info(f'📊 Email Node stats: {status["alerts_sent"]} alerts, {status["alerts_throttled"]} throttled')
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
