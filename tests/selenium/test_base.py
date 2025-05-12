"""
Base class for Selenium tests.
Uses a separate thread to run Flask app instead of LiveServerTestCase.
"""

import os
import time
import unittest
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app import create_app
from app.extensions import db
from app.models import User

# Configuration for tests
class SeleniumTestConfig:
    """Configuration for Selenium tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    LOGIN_VIEW = 'login'
    LOGIN_MESSAGE = 'Please login first'
    LOGIN_MESSAGE_CATEGORY = 'warning'

# Global variables
flask_server = None
server_thread = None

def setup_module():
    """Set up Flask server in a separate thread before running tests."""
    global flask_server, server_thread
    
    # Create Flask app with test config
    flask_server = create_app(SeleniumTestConfig)
    
    # Create a thread to run the server
    server_thread = threading.Thread(target=flask_server.run, 
                                     kwargs={'host': 'localhost', 'port': 5000, 'debug': False, 'use_reloader': False})
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)

def teardown_module():
    """Clean up after all tests are done."""
    # Server thread will be terminated when the main thread exits
    # since it's a daemon thread
    
    # Remove test database file if it exists
    if os.path.exists('test.db'):
        os.remove('test.db')

class SeleniumBaseTest(unittest.TestCase):
    """Base class for Selenium tests without LiveServerTestCase."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class - runs once before all tests in this class."""
        # Start the Flask server if it's not already running
        global server_thread
        if not server_thread or not server_thread.is_alive():
            setup_module()
    
    def setUp(self):
        """Set up each test case."""
        # Create app context
        self.app = flask_server
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Set up test database
        db.create_all()
        
        # Clear any existing test data
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create test user
        test_user = User(username='testuser')
        test_user.password = 'testpassword'
        test_user.security_answer = 'testanswer'  # Must set security_answer
        test_user.fullname = 'Test User'
        test_user.email = 'test@example.com'
        db.session.add(test_user)
        db.session.commit()
        
        # Set up Selenium WebDriver
        options = webdriver.ChromeOptions()
        # For debugging, you can comment this out to see the browser
        options.add_argument('--headless')  # Run in headless mode (no browser UI)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1200, 800)
        self.driver.implicitly_wait(15)  # Implicit wait in seconds
        
        # Base URL for tests
        self.base_url = 'http://localhost:5000'
    
    def tearDown(self):
        """Clean up after each test case."""
        # Save screenshot if test failed
        if hasattr(self, '_outcome') and hasattr(self._outcome, 'errors'):
            # Check if test failed
            for method, error in self._outcome.errors:
                if error:
                    # Test failed, save screenshot
                    try:
                        screenshot_name = f"error_{self._testMethodName}.png"
                        self.driver.save_screenshot(screenshot_name)
                        print(f"Screenshot saved as {screenshot_name}")
                    except Exception as e:
                        print(f"Failed to save screenshot: {e}")
        
        # Quit the driver
        self.driver.quit()
        
        # Clean up the database
        db.session.remove()
        db.drop_all()
        
        # Pop the app context
        self.app_context.pop()
    
    def wait_for(self, by, value, timeout=15):
        """
        Wait for an element to become visible.
        
        Args:
            by: Type of locator (e.g., By.ID, By.CSS_SELECTOR)
            value: Value of the locator
            timeout: Maximum time to wait in seconds
            
        Returns:
            The web element if found
            
        Raises:
            AssertionError: If element not found within timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Timed out waiting for element: {value}")
    
    def wait_for_clickable(self, by, value, timeout=15):
        """
        Wait for an element to become clickable.
        
        Args:
            by: Type of locator
            value: Value of the locator
            timeout: Maximum time to wait in seconds
            
        Returns:
            The web element if found
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Timed out waiting for element to be clickable: {value}")
    
    def login(self, username='testuser', password='testpassword'):
        """
        Helper method to log in a user.
        
        Args:
            username: Username to log in with
            password: Password to log in with
        """
        self.driver.get(f"{self.base_url}/login")
        
        # Fill in login form
        self.driver.find_element(By.ID, 'username').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        
        # Submit form
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        
        # Wait for successful login (sidebar appears)
        self.wait_for(By.CSS_SELECTOR, '.sidebar')