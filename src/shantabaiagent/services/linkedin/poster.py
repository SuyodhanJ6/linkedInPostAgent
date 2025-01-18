from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains
from src.shantabaiagent.services.linkedin.utils import START_POST_SELECTORS, POST_FIELD_SELECTORS, POST_BUTTON_SELECTORS

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
            time.sleep(5)
            
            # Start post button handling remains the same...
            start_post_selectors = START_POST_SELECTORS
            
            start_post_button = None
            for selector in start_post_selectors:
                try:
                    start_post_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
                    
            if not start_post_button:
                raise Exception("Could not find Start a post button")
                
            start_post_button.click()
            time.sleep(3)
            
            # Updated post field handling with more specific selectors and actions
            post_field_selectors = POST_FIELD_SELECTORS
            
            post_field = None
            for selector in post_field_selectors:
                try:
                    post_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    # Try to ensure the element is actually interactable
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", post_field)
                    time.sleep(1)
                    post_field.click()  # Ensure focus
                    break
                except:
                    continue
                    
            if not post_field:
                raise Exception("Could not find post input field")
            
            # Try multiple methods to input text
            try:
                # Method 1: Direct send_keys
                post_field.send_keys(content)
            except:
                try:
                    # Method 2: JavaScript executor
                    self.driver.execute_script("arguments[0].innerHTML = arguments[1]", post_field, content)
                except:
                    try:
                        # Method 3: ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(post_field)
                        actions.click()
                        actions.send_keys(content)
                        actions.perform()
                    except Exception as e:
                        raise Exception(f"Failed to input text: {str(e)}")
            
            time.sleep(2)
            
            # Updated Post button handling with more specific selectors
            post_button_selectors = POST_BUTTON_SELECTORS
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    # Ensure button is actually clickable
                    if post_button.is_enabled() and post_button.is_displayed():
                        break
                except:
                    continue
                    
            if not post_button:
                raise Exception("Could not find Post button")
            
            # Try multiple methods to click the Post button
            try:
                post_button.click()
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", post_button)
                except Exception as e:
                    raise Exception(f"Failed to click Post button: {str(e)}")
            
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"Failed to create post: {str(e)}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()
