from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException, 
    WebDriverException,
    NoSuchElementException
)
import logging
import time
from typing import List
import requests

logger = logging.getLogger(__name__)

class AutomatedPunchSystem:
    def __init__(self):
        self.url = 'http://185.185.127.219:8080/login.jsp'  # Update with your URL
        self.username_input_id = 'login-form-username'
        self.password_input_id = 'login-form-password'
        self.submit_btn_id = 'login-form-submit'
        self.driver_path = "./driver/chromedriver.exe"
        self.api_base_url = "http://localhost:8000/api"  # Update with your API URL

    def setup_driver(self):
        """Setup Chrome driver with proper options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise

    def get_user_credentials(self, mac_addr: str):
        """Get user credentials from API"""
        try:
            response = requests.get(f"{self.api_base_url}/users/{mac_addr}")
            if response.status_code == 200:
                user_data = response.json()
                return user_data['orange_hrm_username'], user_data['orange_hrm_password']
            else:
                logger.error(f"Failed to get credentials for MAC: {mac_addr}")
                return None, None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None, None

    def perform_login(self, driver, username: str, password: str) -> bool:
        """Perform login operation"""
        try:
            # Wait for login form
            wait = WebDriverWait(driver, 10)
            username_input = wait.until(
                EC.presence_of_element_located((By.ID, self.username_input_id))
            )
            password_input = driver.find_element(By.ID, self.password_input_id)
            submit_button = driver.find_element(By.ID, self.submit_btn_id)

            # Clear and fill inputs
            username_input.clear()
            password_input.clear()
            username_input.send_keys(username)
            password_input.send_keys(password)

            # Submit form
            submit_button.click()

            # Wait for login success (adjust based on your success criteria)
            time.sleep(2)
            return True

        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def process_punch_in(self, online_ips: List[str]):
        """Process punch in for online devices"""
        for ip in online_ips:
            try:
                driver = self.setup_driver()
                driver.get(self.url)
                
                # Get credentials for the IP
                username, password = self.get_user_credentials(ip)
                if not username or not password:
                    continue

                if self.perform_login(driver, username, password):
                    # Add your punch in specific logic here
                    logger.info(f"Successfully punched in for IP: {ip}")
                else:
                    logger.error(f"Failed to punch in for IP: {ip}")

            except Exception as e:
                logger.error(f"Error processing punch in for IP {ip}: {str(e)}")
            finally:
                if driver:
                    driver.quit()

    def process_punch_out(self, offline_ips: List[str]):
        """Process punch out for offline devices"""
        for ip in offline_ips:
            try:
                driver = self.setup_driver()
                driver.get(self.url)
                
                # Get credentials for the IP
                username, password = self.get_user_credentials(ip)
                if not username or not password:
                    continue

                if self.perform_login(driver, username, password):
                    # Add your punch out specific logic here
                    logger.info(f"Successfully punched out for IP: {ip}")
                else:
                    logger.error(f"Failed to punch out for IP: {ip}")

            except Exception as e:
                logger.error(f"Error processing punch out for IP {ip}: {str(e)}")
            finally:
                if driver:
                    driver.quit()