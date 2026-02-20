# Copyright 2025 Noah Ploch, Jakub Skupien
# SPDX-License-Identifier: MIT

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from datetime import datetime
import os
import json
import ast


class EmailNode(Node):
    """
    ROS2 Mock Email Node.
    Receives detection events and outputs mock email content to terminal + log files.
    Target: rosie.orchestrate@gmail.com
    """

    def __init__(self):
        super().__init__('email_node')

        # Parameters
        self.declare_parameter('target_email', 'rosie.orchestrate@gmail.com')
        self.declare_parameter('log_dir', '../../logs')
        self.declare_parameter('log_to_file', True)
        self.declare_parameter('input_topic', '/detection/events')

        self.target_email = self.get_parameter('target_email').value
        self.log_dir = os.path.expanduser(
            self.get_parameter('log_dir').value
        )
        self.log_to_file = self.get_parameter('log_to_file').value
        self.input_topic = self.get_parameter('input_topic').value

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Set up log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file_path = os.path.join(
            self.log_dir,
            f'mock_emails_{timestamp}.log'
        )

        # Subscriber
        self.subscription = self.create_subscription(
            String,
            self.input_topic,
            self.detection_callback,
            10
        )

        self.get_logger().info(
            f'EmailNode initialized: target={self.target_email}'
        )
        self.get_logger().info(
            f'   Logging: {"enabled" if self.log_to_file else "disabled"}'
        )
        self.get_logger().info(
            f'   Log file: {self.log_file_path}'
        )

    def detection_callback(self, msg):
        """Handle detection event and generate mock email."""
        try:
            # Parse detection data (safely)
            event_data = ast.literal_eval(msg.data)

            # Generate mock email content
            email_content = self._generate_email(event_data)

            # Output to terminal
            self._output_to_terminal(email_content)

            # Log to file
            if self.log_to_file:
                self._log_to_file(email_content)

        except Exception as e:
            self.get_logger().error(f'Failed to process detection: {e}')

    def _generate_email(self, event_data):
        """Generate mock email content from detection event."""
        timestamp = event_data.get('timestamp', datetime.now().isoformat())
        filename = event_data.get('filename', 'unknown.jpg')
        capture_path = event_data.get('path', 'unknown')
        person_count = event_data.get('person_count', 0)
        confidences = event_data.get('confidences', [])

        email_body = f"""
================================================================================
MOCK EMAIL NOTIFICATION
================================================================================
To: {self.target_email}
From: surveillance-system@ros2.local
Subject: [ALERT] Person Detected - {timestamp}
Timestamp: {timestamp}

--- DETECTION DATA ---
Persons detected: {person_count}
Confidence scores: {', '.join([f'{c:.2f}' for c in confidences]) if confidences else 'N/A'}
Capture filename: {filename}
Capture path: {capture_path}

--- ATTACHMENT ---
[This email would include the detection frame as an attachment]
Filename: {filename}
Full path: {capture_path}

--- SYSTEM INFO ---
ROS2 Camera Surveillance System v0.1.0
Node: email_node
Topic: {self.input_topic}

================================================================================
[MOCK MODE - No email actually sent. Logged to file only.]
================================================================================
"""
        return email_body

    def _output_to_terminal(self, email_content):
        """Output email to terminal with clear formatting."""
        # Use logger for structured output
        self.get_logger().warning('🚨 PERSON DETECTED - MOCK EMAIL SENT')
        
        # Print full email content to stdout for visibility
        print("\n" + "="*80)
        print("                    📧  MOCK EMAIL NOTIFICATION  📧")
        print("="*80)
        print(email_content)
        print("="*80 + "\n")

    def _log_to_file(self, email_content):
        """Append email content to log file."""
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(f"\n[{datetime.now().isoformat()}]\n")
                f.write(email_content)
                f.write("\n" + "-"*80 + "\n")
            self.get_logger().debug(f'Email logged: {self.log_file_path}')
        except Exception as e:
            self.get_logger().error(f'Failed to write log: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = EmailNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Email node stopped by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()