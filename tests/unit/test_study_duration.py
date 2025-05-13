"""
Unit tests for the StudyDuration model.
Tests the creation and management of study duration records.
"""

import unittest
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import User, StudyDuration
from tests.test_config import UnitTestConfig

class TestStudyDuration(unittest.TestCase):
    """Test cases for the StudyDuration model."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app(UnitTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        test_user = User(username='testuser')
        test_user.password = 'testpassword'
        test_user.security_answer = 'testanswer'  # Add security_answer
        db.session.add(test_user)
        db.session.commit()
        
        self.user_id = test_user.id
    
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_study_duration_creation(self):
        """Test creating a study duration record."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=60)
        
        # Create study duration record
        duration = StudyDuration(
            user_id=self.user_id,
            duration=60.0,
            start_time=start_time,
            end_time=now,
            stop_times=2
        )
        db.session.add(duration)
        db.session.commit()
        
        # Retrieve and verify record
        saved_duration = StudyDuration.query.first()
        self.assertEqual(saved_duration.duration, 60.0)
        self.assertEqual(saved_duration.stop_times, 2)
        
        # Fix: Compare only the relevant parts of datetime objects to avoid timezone issues
        self.assertEqual(saved_duration.start_time.replace(tzinfo=None), 
                         start_time.replace(tzinfo=None))
        self.assertEqual(saved_duration.end_time.replace(tzinfo=None), 
                         now.replace(tzinfo=None))
    
    def test_multiple_study_durations(self):
        """Test creating and retrieving multiple study duration records."""
        now = datetime.now(timezone.utc)
        
        # Create three duration records over different days
        for i in range(3):
            day_offset = i * 24  # hours
            start_time = now - timedelta(hours=day_offset + 1)  # 1 hour study
            end_time = now - timedelta(hours=day_offset)
            
            duration = StudyDuration(
                user_id=self.user_id,
                duration=60.0,  # 60 minutes
                start_time=start_time,
                end_time=end_time,
                stop_times=i
            )
            db.session.add(duration)
        
        db.session.commit()
        
        # Verify all records are saved
        durations = StudyDuration.query.all()
        self.assertEqual(len(durations), 3)
        
        # Verify the records have correct stop_times values
        stop_times = sorted([d.stop_times for d in durations])
        self.assertEqual(stop_times, [0, 1, 2])
    
    def test_user_relationship(self):
        """Test the relationship between User and StudyDuration."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=30)
        
        # Create study duration record
        duration = StudyDuration(
            user_id=self.user_id,
            duration=30.0,
            start_time=start_time,
            end_time=now,
            stop_times=0
        )
        db.session.add(duration)
        db.session.commit()
        
        # Test relation from duration to user
        self.assertEqual(duration.user.username, 'testuser')
        
        # Test relation from user to durations
        user = User.query.first()
        self.assertEqual(len(user.study_durations), 1)
        self.assertEqual(user.study_durations[0].duration, 30.0)
    
    def test_string_representation(self):
        """Test the string representation of StudyDuration objects."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=45)
        
        # Create study duration record
        duration = StudyDuration(
            user_id=self.user_id,
            duration=45.0,
            start_time=start_time,
            end_time=now,
            stop_times=1
        )
        
        # Check string representation
        self.assertEqual(repr(duration), '<StudyDuration 45.0 minutes>')


if __name__ == '__main__':
    unittest.main()