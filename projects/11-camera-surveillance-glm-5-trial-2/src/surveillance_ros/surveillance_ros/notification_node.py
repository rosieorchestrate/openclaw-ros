#!/usr/bin/env python3
"""
Notification Node for ROS2
Subscribes to person detection events and sends mock email notifications.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NotificationNode(Node):
    """
    ROS2 node that handles notifications for person detection events.
    
    Subscribes to:
        /detection/person (std_msgs/String): Person detection events (JSON)
        
    Parameters:
        recipient_email: Email recipient (default: rosie.orchestrate@gmail.com)
        sender_email: Email sender (default: surveillance@localhost)
        log_dir: Directory for logs (default: ./logs)
        cooldown_seconds: Minimum time between notifications (default: 10.0)
    """
    
    def __init__(self):
        super().__init__('notification_node')
        
        # Declare parameters
        self.declare_parameter('recipient_email', 'rosie.orchestrate@gmail.com')
        self.declare_parameter('sender_email', 'surveillance@localhost')
        self.declare_parameter('log_dir', './logs')
        self.declare_parameter('cooldown_seconds', 10.0)
        
        # Get parameters
        self.recipient_email = self.get_parameter('recipient_email').value
        self.sender_email = self.get_parameter('sender_email').value
        self.log_dir = Path(self.get_parameter('log_dir').value)
        self.cooldown_seconds = self.get_parameter('cooldown_seconds').value
        
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.email_dir = self.log_dir / 'emails'
        self.email_dir.mkdir(parents=True, exist_ok=True)
        
        # Notification log file
        self.notification_log = self.log_dir / 'notifications.log'
        
        # Subscriber for detection events
        self.subscription = self.create_subscription(
            String,
            '/detection/person',
            self.detection_callback,
            10
        )
        
        # Cooldown tracking
        self.last_notification_time = 0.0
        self.notification_count = 0
        
        self.get_logger().info('Notification Node initialized')
        self.get_logger().info(f'  Recipient: {self.recipient_email}')
        self.get_logger().info(f'  Log directory: {self.log_dir}')
        self.get_logger().info(f'  Cooldown: {self.cooldown_seconds}s')
        
    def detection_callback(self, msg: String):
        """Process detection events and send notifications."""
        try:
            # Parse detection event
            event = json.loads(msg.data)
            
            # Check cooldown
            current_time = self.get_clock().now().nanoseconds / 1e9
            if current_time - self.last_notification_time < self.cooldown_seconds:
                self.get_logger().debug('Skipping notification (cooldown)')
                return
                
            self.last_notification_time = current_time
            self.notification_count += 1
            
            # Send notification
            self.send_notification(event)
            
        except json.JSONDecodeError as e:
            self.get_logger().error(f'Failed to parse detection event: {e}')
        except Exception as e:
            self.get_logger().error(f'Error processing detection: {e}')
            
    def send_notification(self, event: dict):
        """
        Send mock email notification for a detection event.
        
        Args:
            event: Detection event dictionary
        """
        timestamp = event.get('timestamp', datetime.now().isoformat())
        confidence = event.get('max_confidence', 0.0)
        image_path = event.get('image_path', 'N/A')
        detections = event.get('detections', [])
        count = event.get('count', 0)
        
        # Create email content
        email_content = self._create_email_content(
            timestamp=timestamp,
            confidence=confidence,
            image_path=image_path,
            detections=detections,
            count=count
        )
        
        # Save email to file
        email_filename = f"email_{timestamp.replace(':', '-').replace('.', '-')}.txt"
        email_path = self.email_dir / email_filename
        
        with open(email_path, 'w') as f:
            f.write(email_content)
            
        # Save detection JSON
        json_filename = f"detection_{timestamp.replace(':', '-').replace('.', '-')}.json"
        json_path = self.email_dir / json_filename
        
        with open(json_path, 'w') as f:
            json.dump(event, f, indent=2)
            
        # Log to notifications log
        with open(self.notification_log, 'a') as f:
            f.write(f"[{timestamp}] PERSON DETECTED - Confidence: {confidence:.2%} - #{count}\n")
            
        # Print to terminal (mock sending)
        self._print_notification(
            timestamp=timestamp,
            confidence=confidence,
            image_path=image_path,
            email_path=email_path,
            count=count
        )
        
        self.get_logger().info(f'Notification logged: {email_path}')
        
    def _create_email_content(self, timestamp: str, confidence: float, 
                              image_path: str, detections: list, count: int) -> str:
        """Create mock email content."""
        detections_text = '\n'.join([
            f"    - {d['label']}: confidence={d['confidence']:.2%}, bbox={d['bbox']}"
            for d in detections
        ])
        
        return f"""================================================================================
SECURITY ALERT - PERSON DETECTED
================================================================================

From: {self.sender_email}
To: {self.recipient_email}
Subject: 🚨 Security Alert: Person Detected at {timestamp}
Date: {timestamp}

--------------------------------------------------------------------------------
DETECTION DETAILS
--------------------------------------------------------------------------------

Detection #:   {count}
Timestamp:     {timestamp}
Location:      Raspberry Pi Camera
Confidence:    {confidence:.2%}
Image:         {image_path}

Detections:
{detections_text}

--------------------------------------------------------------------------------
MESSAGE
--------------------------------------------------------------------------------

A person has been detected by the surveillance system.

Please review the attached image for verification.

Attachment: {image_path}

================================================================================
This is an automated message from the Raspberry Pi Surveillance System (ROS2).
Do not reply to this email.
================================================================================
"""
        
    def _print_notification(self, timestamp: str, confidence: float, 
                           image_path: str, email_path: Path, count: int):
        """Print notification to terminal."""
        self.get_logger().info('')
        self.get_logger().info('=' * 70)
        self.get_logger().info('🚨 DETECTION ALERT - MOCK EMAIL SENDING')
        self.get_logger().info('=' * 70)
        self.get_logger().info(f'📧 From:       {self.sender_email}')
        self.get_logger().info(f'📧 To:         {self.recipient_email}')
        self.get_logger().info(f'📅 Time:       {timestamp}')
        self.get_logger().info(f'🎯 Confidence: {confidence:.2%}')
        self.get_logger().info(f'📷 Image:      {image_path}')
        self.get_logger().info(f'📊 Detection #: {count}')
        self.get_logger().info('-' * 70)
        self.get_logger().info(f'✅ Email logged to: {email_path}')
        self.get_logger().info('=' * 70)
        self.get_logger().info('')


def main(args=None):
    rclpy.init(args=args)
    
    node = NotificationNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info(f'Shutting down. Total notifications: {node.notification_count}')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()