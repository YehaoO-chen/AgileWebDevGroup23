"""
Selenium tests for profile functionality.
Tests the user profile page, including profile information display and editing.
"""

import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.models import User
from app.extensions import db
from tests.selenium.test_base import SeleniumBaseTest

class TestProfile(SeleniumBaseTest):
    """Test cases for the profile page with Selenium."""
    
    def get_server_url(self):
        """Return the base URL for the server."""
        return self.base_url
    
    def setUp(self):
        """Set up test environment before each test."""
        super().setUp()
        
        # Clean any existing test data and add extra information
        user = User.query.filter_by(username='testuser').first()
        if user:
            # Update user information to ensure all fields have values
            user.fullname = 'Test User Full Name'
            user.email = 'test@example.com'
            user.phone = '1234567890'
            user.address = '123 Test Street, Test City'
            user.major = 'Computer Science'
            user.student_id = 'S12345'
            # Ensure creation time has a value
            if not user.create_time:
                user.create_time = datetime.now()
            db.session.commit()
        
        # Login user
        self.login()
        
        # Navigate to profile page
        self.driver.get(self.get_server_url() + '/profile')
        
        # Wait for page to load
        self.wait_for(By.CLASS_NAME, 'profile-container')
        
        # Wait for JS to load user data
        time.sleep(2)
    
    def scroll_into_view(self, element):
        """Scroll an element into view."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)  # Add a small delay after scrolling
        except Exception as e:
            # If scrolling fails, ignore and continue
            print(f"Warning: Could not scroll element into view: {e}")
    
    def safe_click(self, element):
        """Safely click an element by scrolling it into view first."""
        try:
            self.scroll_into_view(element)
            # Use JavaScript click which is more reliable for intercepted elements
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            # If JavaScript click fails, try normal click
            try:
                element.click()
            except Exception as inner_e:
                self.fail(f"Could not click element: {inner_e}")
    
    def test_profile_display(self):
        """Test that profile information is displayed correctly."""
        # Verify page title
        page_title = self.driver.find_element(By.CLASS_NAME, 'page-title').text
        self.assertEqual(page_title, 'My Profile')
        
        # Verify profile card is displayed
        profile_card = self.driver.find_element(By.CLASS_NAME, 'profile-card')
        self.assertTrue(profile_card.is_displayed())
        
        # Verify personal information area title
        info_title = self.driver.find_element(By.CLASS_NAME, 'info-title').text
        self.assertEqual(info_title, 'Personal Information')
        
        # Verify username display
        username = self.driver.find_element(By.ID, 'username').text
        self.assertEqual(username, 'testuser')
        
        # Verify full name display
        fullname = self.driver.find_element(By.ID, 'fullName').text
        self.assertEqual(fullname, 'Test User Full Name')
        
        # Verify email display
        email = self.driver.find_element(By.ID, 'email').text
        self.assertEqual(email, 'test@example.com')
        
        # Verify phone number display
        phone = self.driver.find_element(By.ID, 'phone').text
        self.assertEqual(phone, '1234567890')
        
        # Verify address display
        address = self.driver.find_element(By.ID, 'address').text
        self.assertEqual(address, '123 Test Street, Test City')
        
        # Verify major display
        major = self.driver.find_element(By.ID, 'major').text
        self.assertEqual(major, 'Computer Science')
        
        # Verify student ID display
        student_id = self.driver.find_element(By.ID, 'studentId').text
        self.assertEqual(student_id, 'S12345')
        
        # Verify profile photo display
        profile_photo = self.driver.find_element(By.ID, 'profilePhoto')
        self.assertTrue(profile_photo.is_displayed())
        # Verify profile photo has src attribute
        self.assertTrue(profile_photo.get_attribute('src') is not None)
        
        # Verify edit button exists
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.assertTrue(edit_btn.is_displayed())
        self.assertEqual(edit_btn.text, 'Edit Profile')
    
    def test_profile_name_and_role(self):
        """Test that profile name and role are displayed correctly."""
        # Verify profile name display
        profile_name = self.driver.find_element(By.ID, 'profileName')
        self.assertTrue(profile_name.is_displayed())
        self.assertNotEqual(profile_name.text, '')
        self.assertNotEqual(profile_name.text, 'Loading...')
        
        # Verify role display (could be student or other)
        profile_role = self.driver.find_element(By.ID, 'profileRole')
        self.assertTrue(profile_role.is_displayed())
        self.assertNotEqual(profile_role.text, '')
        self.assertNotEqual(profile_role.text, 'Loading...')
    
    def test_edit_mode_toggle(self):
        """Test entering and exiting edit mode."""
        # Click edit button
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.safe_click(edit_btn)
        
        # Wait for edit mode to activate
        time.sleep(1)
        
        # Check if edit button text has changed (should be "Save Changes" in edit mode)
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.assertEqual(edit_btn.text, 'Save Changes', "Edit button should change to 'Save Changes' in edit mode")
        
        # Check if cancel button appears
        cancel_btn = self.driver.find_element(By.ID, 'cancelEditBtn')
        self.assertTrue(cancel_btn.is_displayed())
        
        # Click cancel button
        self.safe_click(cancel_btn)
        
        # Wait for edit mode to close
        time.sleep(1)
        
        # Check if edit button text has reverted
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.assertEqual(edit_btn.text, 'Edit Profile', "Edit button should revert to 'Edit Profile' after cancelling")
    
    def test_responsive_layout(self):
        """Test profile page layout at different window sizes."""
        # Test regular desktop size
        self.driver.set_window_size(1200, 800)
        time.sleep(1)
        
        # Get initial element styles
        profile_container = self.driver.find_element(By.CLASS_NAME, 'profile-container')
        profile_card = self.driver.find_element(By.CLASS_NAME, 'profile-card')
        profile_header = self.driver.find_element(By.CLASS_NAME, 'profile-header')
        
        desktop_container_width = profile_container.size['width']
        desktop_card_width = profile_card.size['width']
        desktop_header_display = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", profile_header
        )
        
        # Switch to mobile device size
        self.driver.set_window_size(480, 800)
        time.sleep(1)
        
        # Get styles in mobile size
        mobile_container_width = profile_container.size['width']
        mobile_card_width = profile_card.size['width']
        mobile_header_display = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", profile_header
        )
        
        # Verify responsive layout
        self.assertNotEqual(desktop_container_width, mobile_container_width, 
                          "Container width should change in responsive layout")
        self.assertNotEqual(desktop_card_width, mobile_card_width,
                          "Card width should change in responsive layout")
        
        # Reset window size
        self.driver.set_window_size(1200, 800)