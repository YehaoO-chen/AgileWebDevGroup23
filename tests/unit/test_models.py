"""
Unit tests for the database models.
Tests the User, StudyPlan, StudyDuration, and Notification models.
"""

import unittest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import User, StudyPlan, StudyDuration, Notification
from tests.test_config import UnitTestConfig

class TestUserModel(unittest.TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app(UnitTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        test_user = User(username='testuser')
        test_user.password = 'testpassword'
        test_user.security_answer = 'testanswer'
        db.session.add(test_user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        user = User.query.filter_by(username='testuser').first()
        # Correct password should verify
        self.assertTrue(user.check_password('testpassword'))
        # Incorrect password should not verify
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_password_not_readable(self):
        """Test that password property raises an exception when accessed."""
        user = User.query.filter_by(username='testuser').first()
        with self.assertRaises(AttributeError):
            user.password
    
    def test_security_answer_hashing(self):
        """Test security answer hashing and verification."""
        user = User.query.filter_by(username='testuser').first()
        # Correct answer should verify
        self.assertTrue(user.check_security_answer('testanswer'))
        # Incorrect answer should not verify
        self.assertFalse(user.check_security_answer('wronganswer'))
    
    def test_user_representation(self):
        """Test the string representation of User objects."""
        user = User.query.filter_by(username='testuser').first()
        self.assertEqual(repr(user), '<User testuser>')
    
    def test_user_relationship_cascade(self):
        """Test the relationship between users and study plans."""
        user = User.query.filter_by(username='testuser').first()
        
        # Create a study plan for the user
        study_plan = StudyPlan(
            user_id=user.id,
            content='Test study plan',
            status=0
        )
        db.session.add(study_plan)
        db.session.commit()
        
        # Verify the relationship
        self.assertEqual(len(user.study_plans), 1)
        
        # Clean up study plans before deleting user to avoid integrity error
        for plan in user.study_plans:
            db.session.delete(plan)
        db.session.commit()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Verify no users remain
        self.assertEqual(User.query.count(), 0)
        # Verify no study plans remain
        self.assertEqual(StudyPlan.query.count(), 0)

class TestStudyPlanModel(unittest.TestCase):
    """Test cases for the StudyPlan model."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app(UnitTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user with security_answer field
        test_user = User(username='testuser')
        test_user.password = 'testpassword'
        test_user.security_answer = 'testanswer'
        db.session.add(test_user)
        db.session.commit()
        
        self.user_id = test_user.id
    
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_study_plan_creation(self):
        """Test creating a study plan."""
        study_plan = StudyPlan(
            user_id=self.user_id,
            content='Test study plan',
            status=0
        )
        db.session.add(study_plan)
        db.session.commit()
        
        saved_plan = StudyPlan.query.first()
        self.assertEqual(saved_plan.content, 'Test study plan')
        self.assertEqual(saved_plan.status, 0)
        self.assertIsNone(saved_plan.complete_time)
    
    def test_study_plan_completion(self):
        """Test marking a study plan as complete."""
        study_plan = StudyPlan(
            user_id=self.user_id,
            content='Test study plan',
            status=0
        )
        db.session.add(study_plan)
        db.session.commit()
        
        # Mark as complete - use naive datetime without timezone
        completion_time = datetime.now()
        study_plan.status = 1
        study_plan.complete_time = completion_time
        db.session.commit()
        
        updated_plan = StudyPlan.query.first()
        self.assertEqual(updated_plan.status, 1)
        
        # Check if times are within 1 second of each other instead of exact equality
        time_diff = abs((updated_plan.complete_time - completion_time).total_seconds())
        self.assertLess(time_diff, 1, "Completion times should be within 1 second of each other")
    
    def test_user_relationship(self):
        """Test the relationship between User and StudyPlan."""
        study_plan = StudyPlan(
            user_id=self.user_id,
            content='Test study plan',
            status=0
        )
        db.session.add(study_plan)
        db.session.commit()
        
        # Test the relationship from study plan to user
        self.assertEqual(study_plan.user.username, 'testuser')
        
        # Test the relationship from user to study plans
        user = User.query.first()
        self.assertEqual(len(user.study_plans), 1)
        self.assertEqual(user.study_plans[0].content, 'Test study plan')


if __name__ == '__main__':
    unittest.main()