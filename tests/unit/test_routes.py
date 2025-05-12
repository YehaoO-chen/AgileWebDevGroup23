"""
Unit tests for the application routes.
Tests that routes return correct status codes and content.
"""

import unittest
from flask import url_for
from flask_login import current_user
from app import create_app
from app.extensions import db
from app.models import User
from tests.test_config import UnitTestConfig

class TestRoutes(unittest.TestCase):
    """Test cases for Flask routes."""
    
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
    
    def login(self, username='testuser', password='testpassword'):
        """Helper method to log in a user."""
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def test_index_route(self):
        """Test the index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ProcrastiNo', response.data)
    
    def test_login_route_get(self):
        """Test GET request to login route."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Please log in to your account', response.data)
    
    def test_signup_route_get(self):
        """Test GET request to signup route."""
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)
        self.assertIn(b'Create your ProcrastiNo account', response.data)
    
    def test_reset_route_get(self):
        """Test GET request to reset route."""
        response = self.client.get('/reset')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reset Password', response.data)
        self.assertIn(b'Security Question', response.data)
    
    def test_protected_routes_redirect_when_not_logged_in(self):
        """Test that protected routes redirect to login when not logged in."""
        protected_routes = [
            '/mainpage',
            '/studyplan',
            '/dashboard',
            '/notification',
            '/profile'
        ]
        
        for route in protected_routes:
            response = self.client.get(route, follow_redirects=False)
            self.assertEqual(response.status_code, 302)  # Should redirect
            
            # Check the response.location directly - don't require a specific format for the redirect URL
            # Just verify it contains 'login'
            self.assertIn('login', response.location)
    
    def test_protected_routes_accessible_after_login(self):
        """Test that protected routes are accessible after login."""
        # First login
        self.login()
        
        protected_routes = [
            '/mainpage',
            '/studyplan',
            '/dashboard',
            '/notification',
            '/profile'
        ]
        
        for route in protected_routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200)
    
    def test_ajax_content_loading(self):
        """Test that routes handle AJAX requests correctly."""
        # First login
        self.login()
        
        # Set header to simulate AJAX request
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        # Test studyplan route with AJAX
        response = self.client.get('/studyplan', headers=headers)
        self.assertEqual(response.status_code, 200)
        # Should not include base layout for AJAX requests
        self.assertNotIn(b'<!DOCTYPE html>', response.data)
        self.assertIn(b'Study Plan', response.data)
        
        # Test dashboard route with AJAX
        response = self.client.get('/dashboard', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'<!DOCTYPE html>', response.data)
        
        # Test notification route with AJAX
        response = self.client.get('/notification', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'<!DOCTYPE html>', response.data)
    
    def test_logout_route(self):
        """Test the logout route."""
        # First login
        self.login()
        
        # Then logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify logout message
        self.assertIn(b'You have been logged out', response.data)
        
        # Verify redirect to login page
        self.assertIn(b'Login', response.data)


if __name__ == '__main__':
    unittest.main()