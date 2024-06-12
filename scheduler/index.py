from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from helper import get_online_offline_devices, get_operation_type
from crontab import CronTab
import schedule
import logging
import datetime
# Params
URL = 'http://185.185.127.219:8080/login.jsp'   # Url of the orange website
USERNAME_INPUT_ID = 'login-form-username'       # Id of username input element
PASSWORD_INPUT_ID = 'login-form-password'       # Id of password input element
SUBMIT_BTN_ID = 'login-form-submit'             # Id of submit btn
username='phurba.sherpa'
password='Phurb@12'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():

    online_ips, offline_ips = get_online_offline_devices(['192.168.1.68'])
    operation_type = get_operation_type()

    if operation_type == 'PI':
        print('Punch in process started...')
        print('Punching in for ips', online_ips)
    elif operation_type == 'PO':
        print('Punch out process started...')
        print('Punching out for ips', offline_ips)

    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.get(URL)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, USERNAME_INPUT_ID))
    )

    username_input_el = driver.find_element(by=By.ID, value=USERNAME_INPUT_ID)
    password_input_el = driver.find_element(by=By.ID, value=PASSWORD_INPUT_ID)
    
    # clear
    username_input_el.clear()
    password_input_el.clear()
    
    # type
    username_input_el.send_keys(username)
    password_input_el.send_keys(password)

    # submit
    driver.find_element(by=By.ID, value=SUBMIT_BTN_ID).click()
    heading = driver.find_element(By.TAG_NAME, 'h1')
    title = heading.text

    time.sleep(10)
    driver.quit()
    print(title)
if __name__=="__main__": 
    main() 

def job():
    now = datetime.datetime.now()
    print(now)
    current_time = now.time()
    print(current_time)
    if now.weekday() < 5:  # Monday to Friday 1 is monday 
        if (datetime.time(10, 0) <= current_time <= datetime.time(11, 15)) or (datetime.time(18, 0) <= current_time <= datetime.time(19, 15)):
            logging.info("Job triggered within allowed time interval")
            print("job is triggered")

# Schedule the job every 15 minutes
schedule.every(15).minutes.do(job)

# Run scheduler in a loop
while True:
    schedule.run_pending()
    time.sleep(1)

