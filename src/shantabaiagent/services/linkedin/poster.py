from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

class LinkedInPoster:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-notifications')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)
        return True
    
    def login_to_linkedin(self, email: str, password: str) -> bool:
        try:
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)
            
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def create_post(self, content: str) -> bool:
        try:
            # Go to feed page
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(3)
            
            # Click post button
            post_button = self.driver.find_element(By.CSS_SELECTOR, "button.artdeco-button.artdeco-button--muted")
            post_button.click()
            time.sleep(2)
            
            # Enter content
            post_field = self.driver.find_element(By.CSS_SELECTOR, "div.ql-editor")
            post_field.send_keys(content)
            time.sleep(2)
            
            # Click share button
            share_button = self.driver.find_element(By.CSS_SELECTOR, "button.share-actions__primary-action")
            share_button.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"Failed to create post: {str(e)}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()
