#!/usr/bin/env python3
"""
Notification Handler Module
Handles email notifications (mocked) for person detection events
"""

import logging
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class DetectionEvent:
    """Represents a detection event."""
    timestamp: str
    confidence: float
    image_path: str
    location: str = "Raspberry Pi Camera"
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "image_path": self.image_path,
            "location": self.location
        }


class NotificationHandler:
    """
    Handles notifications for detection events.
    Mocks email sending by logging to terminal and files.
    """
    
    def __init__(
        self,
        recipient_email: str,
        sender_email: str,
        log_dir: str = "logs",
        captures_dir: str = "captures",
        project_root: str = None
    ):
        self.recipient_email = recipient_email
        self.sender_email = sender_email
        
        # Resolve paths
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Default to parent of src directory
            self.project_root = Path(__file__).parent.parent
            
        self.log_dir = self.project_root / log_dir
        self.captures_dir = self.project_root / captures_dir
        self.email_log_dir = self.log_dir / "emails"
        
        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        self.email_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Notification log file
        self.notification_log = self.log_dir / "notifications.log"
        
        logger.info(f"NotificationHandler initialized")
        logger.info(f"  Log dir: {self.log_dir}")
        logger.info(f"  Captures dir: {self.captures_dir}")
        logger.info(f"  Recipient: {self.recipient_email}")
        
    def send_detection_notification(
        self,
        event: DetectionEvent,
        image_data: bytes = None
    ) -> bool:
        """
        Send (mock) notification for a detection event.
        
        Args:
            event: DetectionEvent with detection details
            image_data: Optional image bytes to attach
            
        Returns:
            True if notification was logged successfully
        """
        try:
            # Create email content
            email_content = self._create_email_content(event)
            
            # Save email to log file
            email_filename = f"email_{event.timestamp.replace(':', '-').replace('.', '-')}.txt"
            email_path = self.email_log_dir / email_filename
            
            with open(email_path, 'w') as f:
                f.write(email_content)
            
            # Save detection event as JSON
            event_filename = f"detection_{event.timestamp.replace(':', '-').replace('.', '-')}.json"
            event_path = self.email_log_dir / event_filename
            
            with open(event_path, 'w') as f:
                json.dump(event.to_dict(), f, indent=2)
            
            # Log to main notification log
            with open(self.notification_log, 'a') as f:
                f.write(f"[{event.timestamp}] PERSON DETECTED - Confidence: {event.confidence:.2f}\n")
            
            # Print to terminal (mock sending)
            self._print_notification(event, email_path)
            
            logger.info(f"Detection notification logged: {email_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def _create_email_content(self, event: DetectionEvent) -> str:
        """Create the email content."""
        content = f"""================================================================================
SECURITY ALERT - PERSON DETECTED
================================================================================

From: {self.sender_email}
To: {self.recipient_email}
Subject: 🚨 Security Alert: Person Detected at {event.timestamp}
Date: {event.timestamp}

--------------------------------------------------------------------------------
DETECTION DETAILS
--------------------------------------------------------------------------------

Timestamp:    {event.timestamp}
Location:     {event.location}
Confidence:   {event.confidence:.2%}
Image:        {event.image_path}

--------------------------------------------------------------------------------
MESSAGE
--------------------------------------------------------------------------------

A person has been detected by the surveillance system.

Please review the attached image for verification.

Attachment: {event.image_path}

================================================================================
This is an automated message from the Raspberry Pi Surveillance System.
Do not reply to this email.
================================================================================
"""
        return content
    
    def _print_notification(self, event: DetectionEvent, email_path: Path) -> None:
        """Print notification to terminal (mock email sending)."""
        print("\n" + "=" * 80)
        print("🚨 DETECTION ALERT - MOCK EMAIL SENDING")
        print("=" * 80)
        print(f"📧 From:    {self.sender_email}")
        print(f"📧 To:      {self.recipient_email}")
        print(f"📅 Time:    {event.timestamp}")
        print(f"🎯 Confidence: {event.confidence:.2%}")
        print(f"📷 Image:   {event.image_path}")
        print("-" * 80)
        print(f"✅ Email logged to: {email_path}")
        print("=" * 80 + "\n")
    
    def get_recent_notifications(self, count: int = 10) -> list:
        """Get recent notifications from the log."""
        notifications = []
        
        if not self.notification_log.exists():
            return notifications
            
        with open(self.notification_log, 'r') as f:
            lines = f.readlines()
            
        for line in lines[-count:]:
            if line.strip():
                notifications.append(line.strip())
                
        return notifications


if __name__ == "__main__":
    # Test the notification handler
    logging.basicConfig(level=logging.INFO)
    
    handler = NotificationHandler(
        recipient_email="rosie.orchestrate@gmail.com",
        sender_email="surveillance@localhost",
        log_dir="logs",
        captures_dir="captures"
    )
    
    # Create a test event
    event = DetectionEvent(
        timestamp=datetime.now().isoformat(),
        confidence=0.85,
        image_path="captures/test_detection.jpg"
    )
    
    # Send notification
    handler.send_detection_notification(event)
    print("\n✅ Notification handler test complete")