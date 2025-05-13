"""
Selenium tests for authentication functionality.
Tests user sign-up, login, logout, and password reset with a Flask app running in a separate thread.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.selenium.test_base import SeleniumBaseTest

class TestAuthentication(SeleniumBaseTest):
    """Test cases for authentication pages with Selenium."""
    
    def safe_click(self, element):
        """Safely click an element by scrolling it into view first and using JavaScript."""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)  # Add a small delay after scrolling
        self.driver.execute_script("arguments[0].click();", element)
    
    def test_login_success(self):
        """Test successful login flow."""
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        
        # Verify page title and form exists
        self.assertEqual('Login - ProcrastiNo', self.driver.title)
        self.assertTrue(self.driver.find_element(By.ID, 'username').is_displayed())
        
        # Fill login form
        self.driver.find_element(By.ID, 'username').send_keys('testuser')
        self.driver.find_element(By.ID, 'password').send_keys('testpassword')
        
        # Submit form using JavaScript click
        submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(submit_button)
        
        # Wait for and verify successful login (sidebar appears)
        self.wait_for(By.CSS_SELECTOR, '.sidebar')
        
        # Verify we're on a logged-in page by checking for the sidebar
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, '.sidebar').is_displayed())
    
    def test_login_invalid_password(self):
        """Test login with invalid password shows error message."""
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        
        # Fill form with invalid password
        self.driver.find_element(By.ID, 'username').send_keys('testuser')
        self.driver.find_element(By.ID, 'password').send_keys('wrongpassword')
        
        # Submit form using JavaScript click
        submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(submit_button)
        
        # Wait for and verify error message
        self.wait_for(By.CLASS_NAME, 'alert-danger')
        self.assertIn('Invalid password', self.driver.page_source)
    
    def test_signup_new_user(self):
        """Test creating a new user account."""
        # Navigate to signup page
        self.driver.get(f"{self.base_url}/signup")
        
        # Verify page title and form exists
        self.assertEqual('Sign Up - ProcrastiNo', self.driver.title)
        self.assertTrue(self.driver.find_element(By.ID, 'username').is_displayed())
        
        # Fill signup form with a unique username
        unique_username = f'newuser{int(time.time())}'  # Add timestamp to make it unique
        self.driver.find_element(By.ID, 'username').send_keys(unique_username)
        self.driver.find_element(By.ID, 'password').send_keys('newpassword')
        self.driver.find_element(By.ID, 'security_answer').send_keys('newanswer')
        
        # Submit form using JavaScript click
        submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(submit_button)
        
        # Wait for and verify success message
        self.wait_for(By.CLASS_NAME, 'alert-success')
        self.assertIn('Signup successful', self.driver.page_source)
        
        # Login with new account
        self.driver.find_element(By.ID, 'username').send_keys(unique_username)
        self.driver.find_element(By.ID, 'password').send_keys('newpassword')
        
        # Submit login form
        login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(login_button)
        
        # Verify successful login by checking for sidebar
        self.wait_for(By.CSS_SELECTOR, '.sidebar')
    
    def test_signup_duplicate_username(self):
        """Test signup with existing username shows error."""
        # Navigate to signup page
        self.driver.get(f"{self.base_url}/signup")
        
        # Fill form with existing username
        self.driver.find_element(By.ID, 'username').send_keys('testuser')  # Existing user
        self.driver.find_element(By.ID, 'password').send_keys('newpassword')
        self.driver.find_element(By.ID, 'security_answer').send_keys('newanswer')
        
        # Submit form using JavaScript click
        submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(submit_button)
        
        # Wait for and verify error message
        self.wait_for(By.CLASS_NAME, 'alert-danger')
        self.assertIn('Username already exists', self.driver.page_source)
    
    def test_password_reset(self):
        """Test password reset functionality."""
        # Navigate to reset page
        self.driver.get(f"{self.base_url}/reset")
        
        # Verify page title and form exists
        self.assertEqual('Reset Password - ProcrastiNo', self.driver.title)
        
        # Fill reset form
        self.driver.find_element(By.ID, 'username').send_keys('testuser')
        self.driver.find_element(By.ID, 'security_answer').send_keys('testanswer')
        self.driver.find_element(By.ID, 'new_password').send_keys('newpassword')
        
        # Submit form using JavaScript click
        submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(submit_button)
        
        # Wait for and verify success message
        self.wait_for(By.CLASS_NAME, 'alert-success')
        self.assertIn('Password reset successful', self.driver.page_source)
        
        # Login with new password
        self.driver.find_element(By.ID, 'username').send_keys('testuser')
        self.driver.find_element(By.ID, 'password').send_keys('newpassword')
        
        # Submit login form
        login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        self.safe_click(login_button)
        
        # Verify successful login
        self.wait_for(By.CSS_SELECTOR, '.sidebar')