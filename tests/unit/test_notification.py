"""
Unit tests for the Notification model.
Tests the creation and management of notification records.
"""

import unittest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models import User, Notification
from tests.test_config import UnitTestConfig

class TestNotification(unittest.TestCase):
    """Test cases for the Notification model."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app(UnitTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create two test users
        user1 = User(username='sender')
        user1.password = 'password1'
        user1.security_answer = 'answer1'  # Add security_answer
        
        user2 = User(username='receiver')
        user2.password = 'password2'
        user2.security_answer = 'answer2'  # Add security_answer
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        self.sender_id = user1.id
        self.receiver_id = user2.id
    
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_notification_creation(self):
        """Test creating a notification."""
        # Create notification
        notification = Notification(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content='Test notification',
            status=0  # Unread
        )
        db.session.add(notification)
        db.session.commit()
        
        # Retrieve and verify notification
        saved_notification = Notification.query.first()
        self.assertEqual(saved_notification.content, 'Test notification')
        self.assertEqual(saved_notification.status, 0)
        self.assertEqual(saved_notification.sender_id, self.sender_id)
        self.assertEqual(saved_notification.receiver_id, self.receiver_id)
    
    def test_notification_status_update(self):
        """Test updating a notification's status."""
        # Create notification
        notification = Notification(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content='Test notification',
            status=0  # Unread
        )
        db.session.add(notification)
        db.session.commit()
        
        # Update status to read
        notification.status = 2  # Read
        db.session.commit()
        
        # Verify update
        updated_notification = Notification.query.first()
        self.assertEqual(updated_notification.status, 2)
    
    def test_notification_default_values(self):
        """Test notification default values."""
        notification = Notification(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content='Test notification'
        )
        db.session.add(notification)
        db.session.commit()
        
        saved_notification = Notification.query.first()
        self.assertEqual(saved_notification.status, 0)  # Default is unread (0)
        self.assertIsNotNone(saved_notification.send_time)  # send_time should be auto-set
    
    def test_notification_relationships(self):
        """Test relationships between User and Notification."""
        # Create notification
        notification = Notification(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content='Test notification',
            status=0
        )
        db.session.add(notification)
        db.session.commit()
        
        # Verify sender relationship
        self.assertEqual(notification.sender.username, 'sender')
        
        # Verify receiver relationship
        self.assertEqual(notification.receiver.username, 'receiver')
        
        # Verify sent_notifications relationship
        sender = User.query.filter_by(username='sender').first()
        self.assertEqual(len(sender.sent_notifications), 1)
        self.assertEqual(sender.sent_notifications[0].content, 'Test notification')
        
        # Verify received_notifications relationship
        receiver = User.query.filter_by(username='receiver').first()
        self.assertEqual(len(receiver.received_notifications), 1)
        self.assertEqual(receiver.received_notifications[0].content, 'Test notification')
    
    def test_notification_string_representation(self):
        """Test the string representation of Notification objects."""
        notification = Notification(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content='Test notification'
        )
        
        # Verify string representation
        expected_repr = f'<Notification from {self.sender_id} to {self.receiver_id}>'
        self.assertEqual(repr(notification), expected_repr)


if __name__ == '__main__':
    unittest.main()