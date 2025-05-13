"""
Configuration for the test suite.
This file contains shared configurations for the test suite.
"""

import os

# Unit Test Configuration
class UnitTestConfig:
    """Configuration for unit tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SECRET_KEY = 'test-secret-key'
    LOGIN_VIEW = 'login'
    LOGIN_MESSAGE = 'Please login first'
    LOGIN_MESSAGE_CATEGORY = 'warning'

# Selenium Test Configuration
class SeleniumTestConfig:
    """Configuration for Selenium tests."""
    TESTING = True
    # Using SQLite file for selenium tests to persist between requests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    LOGIN_VIEW = 'login'
    LOGIN_MESSAGE = 'Please login first'
    LOGIN_MESSAGE_CATEGORY = 'warning'
    SERVER_NAME = 'localhost:5000'  # Server hostname for live testing

# Test Data
TEST_USER = {
    'username': 'testuser',
    'password': 'testpassword',
    'security_answer': 'testanswer',
    'fullname': 'Test User',
    'email': 'test@example.com'
}

# Helper function to clean up test database
def cleanup_database():
    """Remove test database if it exists."""
    if os.path.exists('test.db'):
        os.remove('test.db')