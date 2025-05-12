"""
Unit tests for authentication functionality.
Tests login, signup, and password reset functionality.
"""

import unittest
from flask import url_for, session
from app import create_app
from app.extensions import db
from app.models import User
from tests.test_config import UnitTestConfig

class TestAuth(unittest.TestCase):
    """Test cases for authentication functionality."""
    
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
        
        # Create test client
        self.client = self.app.test_client()
        
        # Enable url_for in tests
        self.app.config['SERVER_NAME'] = 'localhost'
        self.app.config['PREFERRED_URL_SCHEME'] = 'http'
        self.app_context = self.app.test_request_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop()
        db.session.remove()
        db.drop_all()
    
    def test_signup_success(self):
        """Test successful user registration."""
        response = self.client.post('/signup', data={
            'username': 'newuser',
            'password': 'newpassword',
            'security_answer': 'newanswer'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify user is created in database
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('newpassword'))
        self.assertTrue(user.check_security_answer('newanswer'))
        
        # Verify redirect message
        self.assertIn(b'Signup successful', response.data)
    
    def test_signup_duplicate_username(self):
        """Test registration with existing username fails."""
        response = self.client.post('/signup', data={
            'username': 'testuser',  # Duplicate username
            'password': 'newpassword',
            'security_answer': 'newanswer'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already exists', response.data)
    
    def test_login_success(self):
        """Test successful login."""
        # Check login page is accessible
        login_get = self.client.get('/login')
        self.assertEqual(login_get.status_code, 200)
        
        # Test login post - Modified to check redirection instead of message
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Instead of checking for login success message, check that we redirected to a page with a sidebar
        self.assertIn(b'<nav class="sidebar">', response.data)
    
    def test_login_invalid_password(self):
        """Test login with invalid password fails."""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid password', response.data)
    
    def test_login_invalid_username(self):
        """Test login with non-existent username fails."""
        response = self.client.post('/login', data={
            'username': 'nonexistentuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User not found', response.data)
    
    def test_logout(self):
        """Test user logout."""
        # First login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        # Then logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out', response.data)
    
    def test_password_reset(self):
        """Test password reset functionality."""
        response = self.client.post('/reset', data={
            'username': 'testuser',
            'security_answer': 'testanswer',
            'new_password': 'newpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password reset successful', response.data)
        
        # Verify password is updated
        user = User.query.filter_by(username='testuser').first()
        self.assertTrue(user.check_password('newpassword'))
    
    def test_password_reset_invalid_answer(self):
        """Test password reset with incorrect security answer fails."""
        response = self.client.post('/reset', data={
            'username': 'testuser',
            'security_answer': 'wronganswer',
            'new_password': 'newpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incorrect security answer', response.data)
        
        # Verify password is not updated
        user = User.query.filter_by(username='testuser').first()
        self.assertFalse(user.check_password('newpassword'))
        self.assertTrue(user.check_password('testpassword'))


if __name__ == '__main__':
    unittest.main()