"""
Selenium tests for main page functionality.
Tests the main page features with a live server including the timer and task list.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.selenium.test_base import SeleniumBaseTest

class TestMainPage(SeleniumBaseTest):
    """Test cases for the main page with Selenium."""
    
    def setUp(self):
        """Set up test environment before each test."""
        super().setUp()
        
        # Login first (using helper method from parent class)
        self.login()
        
        # Navigate to main page - fixed to use direct URL instead of get_server_url()
        self.driver.get("http://localhost:5000/mainpage")
        
        # Wait for page to load
        self.wait_for(By.ID, 'focus-time')
    
    def test_focus_timer_display(self):
        """Test that focus timer elements are displayed correctly."""
        # Verify timer setup elements are present
        self.assertTrue(self.driver.find_element(By.ID, 'focus-time').is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, 'break-time').is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, 'start-btn').is_displayed())
        
        # Verify default values
        focus_time = self.driver.find_element(By.ID, 'focus-time').get_attribute('value')
        break_time = self.driver.find_element(By.ID, 'break-time').get_attribute('value')
        
        self.assertEqual(focus_time, '50')  # Default focus time is 50 min
        self.assertEqual(break_time, '10')  # Default break time is 10 min
    
    def test_timer_controls(self):
        """Test the timer increment/decrement controls."""
        focus_time = self.driver.find_element(By.ID, 'focus-time')
        initial_value = int(focus_time.get_attribute('value'))
        
        # Test increment button
        self.driver.find_element(By.ID, 'focus-plus').click()
        new_value = int(focus_time.get_attribute('value'))
        self.assertEqual(new_value, initial_value + 1)
        
        # Test decrement button
        self.driver.find_element(By.ID, 'focus-minus').click()
        new_value = int(focus_time.get_attribute('value'))
        self.assertEqual(new_value, initial_value)
        
        # Test direct input
        focus_time.clear()
        focus_time.send_keys('25')
        self.assertEqual(focus_time.get_attribute('value'), '25')
    
    def test_timer_start(self):
        """Test starting the timer."""
        # Set a short focus time for testing
        focus_time = self.driver.find_element(By.ID, 'focus-time')
        focus_time.clear()
        focus_time.send_keys('5')  # 5 minutes
        
        # Start the timer
        self.driver.find_element(By.ID, 'start-btn').click()
        
        # Verify timer is visible and running
        self.wait_for(By.ID, 'floating-timer')
        self.assertTrue(self.driver.find_element(By.ID, 'countdown-display').is_displayed())
        
        # Wait a moment and check that time is decreasing
        time.sleep(2)
        countdown_text = self.driver.find_element(By.ID, 'countdown-display').text
        # You might want to add assertions here to verify the timer is counting down