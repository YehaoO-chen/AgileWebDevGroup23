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
        
        # 清理任何可能存在的测试数据并添加额外信息
        user = User.query.filter_by(username='testuser').first()
        if user:
            # 更新用户信息以确保所有字段都有值
            user.fullname = 'Test User Full Name'
            user.email = 'test@example.com'
            user.phone = '1234567890'
            user.address = '123 Test Street, Test City'
            user.major = 'Computer Science'
            user.student_id = 'S12345'
            # 确保创建时间有值
            if not user.create_time:
                user.create_time = datetime.now()
            db.session.commit()
        
        # 登录用户
        self.login()
        
        # 导航到个人资料页面
        self.driver.get(self.get_server_url() + '/profile')
        
        # 等待页面加载
        self.wait_for(By.CLASS_NAME, 'profile-container')
        
        # 等待JS加载用户数据
        time.sleep(2)
    
    def scroll_into_view(self, element):
        """Scroll an element into view."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)  # 滚动后添加短暂延迟
        except Exception as e:
            # 如果滚动失败，忽略并继续
            print(f"Warning: Could not scroll element into view: {e}")
    
    def safe_click(self, element):
        """Safely click an element by scrolling it into view first."""
        try:
            self.scroll_into_view(element)
            # 使用JavaScript点击，这对于被拦截的元素更可靠
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            # 如果JavaScript点击失败，尝试普通点击
            try:
                element.click()
            except Exception as inner_e:
                self.fail(f"Could not click element: {inner_e}")
    
    def test_profile_display(self):
        """Test that profile information is displayed correctly."""
        # 验证页面标题
        page_title = self.driver.find_element(By.CLASS_NAME, 'page-title').text
        self.assertEqual(page_title, 'My Profile')
        
        # 验证个人资料卡片显示
        profile_card = self.driver.find_element(By.CLASS_NAME, 'profile-card')
        self.assertTrue(profile_card.is_displayed())
        
        # 验证个人信息区域标题
        info_title = self.driver.find_element(By.CLASS_NAME, 'info-title').text
        self.assertEqual(info_title, 'Personal Information')
        
        # 验证用户名显示
        username = self.driver.find_element(By.ID, 'username').text
        self.assertEqual(username, 'testuser')
        
        # 验证全名显示
        fullname = self.driver.find_element(By.ID, 'fullName').text
        self.assertEqual(fullname, 'Test User Full Name')
        
        # 验证电子邮件显示
        email = self.driver.find_element(By.ID, 'email').text
        self.assertEqual(email, 'test@example.com')
        
        # 验证电话号码显示
        phone = self.driver.find_element(By.ID, 'phone').text
        self.assertEqual(phone, '1234567890')
        
        # 验证地址显示
        address = self.driver.find_element(By.ID, 'address').text
        self.assertEqual(address, '123 Test Street, Test City')
        
        # 验证专业显示
        major = self.driver.find_element(By.ID, 'major').text
        self.assertEqual(major, 'Computer Science')
        
        # 验证学生ID显示
        student_id = self.driver.find_element(By.ID, 'studentId').text
        self.assertEqual(student_id, 'S12345')
        
        # 验证头像显示
        profile_photo = self.driver.find_element(By.ID, 'profilePhoto')
        self.assertTrue(profile_photo.is_displayed())
        # 验证头像有src属性
        self.assertTrue(profile_photo.get_attribute('src') is not None)
        
        # 验证编辑按钮存在
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.assertTrue(edit_btn.is_displayed())
        self.assertEqual(edit_btn.text, 'Edit Profile')
    
    def test_profile_name_and_role(self):
        """Test that profile name and role are displayed correctly."""
        # 验证个人资料名称显示
        profile_name = self.driver.find_element(By.ID, 'profileName')
        self.assertTrue(profile_name.is_displayed())
        self.assertNotEqual(profile_name.text, '')
        self.assertNotEqual(profile_name.text, 'Loading...')
        
        # 验证角色显示（可能是学生或其他）
        profile_role = self.driver.find_element(By.ID, 'profileRole')
        self.assertTrue(profile_role.is_displayed())
        self.assertNotEqual(profile_role.text, '')
        self.assertNotEqual(profile_role.text, 'Loading...')
    
    def test_edit_mode_toggle(self):
        """Test entering and exiting edit mode."""
        # 点击编辑按钮
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.safe_click(edit_btn)
        
        # 等待一段时间让编辑模式激活
        time.sleep(1)
        
        # 检查编辑按钮文本是否更改（假设在编辑模式下文本会变为"Save"）
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.assertEqual(edit_btn.text, 'Save Changes', "Edit button should change to 'Save Changes' in edit mode")
        
        # 检查取消按钮是否出现
        cancel_btn = self.driver.find_element(By.ID, 'cancelEditBtn')
        self.assertTrue(cancel_btn.is_displayed())
        
        # 点击取消按钮
        self.safe_click(cancel_btn)
        
        # 等待一段时间让编辑模式关闭
        time.sleep(1)
        
        # 检查编辑按钮文本是否恢复
        edit_btn = self.driver.find_element(By.ID, 'editProfileBtn')
        self.assertEqual(edit_btn.text, 'Edit Profile', "Edit button should revert to 'Edit Profile' after cancelling")
    
    def test_avatar_change_button(self):
        """Test avatar change button functionality."""
        # 获取头像更改按钮
        avatar_btn = self.driver.find_element(By.ID, 'changePhotoBtn')
        self.assertTrue(avatar_btn.is_displayed())
        
        # 验证上传输入元素存在且隐藏
        avatar_upload = self.driver.find_element(By.ID, 'avatarUpload')
        self.assertFalse(avatar_upload.is_displayed())
        
        # 因为我们不能直接测试文件上传对话框（系统级别），
        # 所以我们只验证点击按钮会触发某些事件
        
        # 使用JavaScript监听点击事件
        self.driver.execute_script("""
            window.avatarButtonClicked = false;
            var originalClick = HTMLElement.prototype.click;
            
            // 重写文件输入的点击方法以跟踪
            document.getElementById('avatarUpload').click = function() {
                window.avatarButtonClicked = true;
                // 不实际调用原始点击以避免打开文件对话框
            };
        """)
        
        # 点击头像更改按钮
        self.safe_click(avatar_btn)
        
        # 检查我们的跟踪变量
        clicked = self.driver.execute_script("return window.avatarButtonClicked;")
        self.assertTrue(clicked, "Avatar upload input should be triggered when change button is clicked")
    
    def test_responsive_layout(self):
        """Test profile page layout at different window sizes."""
        # 测试常规桌面尺寸
        self.driver.set_window_size(1200, 800)
        time.sleep(1)
        
        # 获取元素初始样式
        profile_container = self.driver.find_element(By.CLASS_NAME, 'profile-container')
        profile_card = self.driver.find_element(By.CLASS_NAME, 'profile-card')
        profile_header = self.driver.find_element(By.CLASS_NAME, 'profile-header')
        
        desktop_container_width = profile_container.size['width']
        desktop_card_width = profile_card.size['width']
        desktop_header_display = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", profile_header
        )
        
        # 切换到移动设备尺寸
        self.driver.set_window_size(480, 800)
        time.sleep(1)
        
        # 获取移动尺寸下的样式
        mobile_container_width = profile_container.size['width']
        mobile_card_width = profile_card.size['width']
        mobile_header_display = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", profile_header
        )
        
        # 验证响应式布局
        self.assertNotEqual(desktop_container_width, mobile_container_width, 
                          "Container width should change in responsive layout")
        self.assertNotEqual(desktop_card_width, mobile_card_width,
                          "Card width should change in responsive layout")
        
        # 重置窗口大小
        self.driver.set_window_size(1200, 800)