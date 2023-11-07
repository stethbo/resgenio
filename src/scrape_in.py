import os
import sys
import logging
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()
URL = 'https://www.linkedin.com'
USER_URL = "https://www.linkedin.com/in/stefan-borek-662510236/"
USERNAME = os.environ.get("IN_USERNAME")
PASSWORD = os.environ.get("IN_PASSWORD")

def log_in_vol_1(driver):
    username_input = driver.find_element(By.ID, 'email-or-phone')
    password_input = driver.find_element(By.ID, 'password')
    login_button = driver.find_element(By.XPATH, '//*[@id="public_profile_contextual-sign-in_sign-in-modal"]/div/section/div/div/form/div[2]/button')
    logger.info("Found log in field on pop up🍾")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    logger.info('Keys sent to form🔑')
    login_button.click()
    time.sleep(1)

    return driver


def log_in_vol_2(driver):
    
    username_input = driver.find_element(By.XPATH, '//*[@id="session_key"]')
    password_input = driver.find_element(By.XPATH, '//*[@id="session_password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/div/form/div[2]/button')
    logger.info("Found log in field on pop up🍾")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    logger.info('Keys sent to form🔑')
    login_button.click()
    time.sleep(1)

    return driver


def log_in_vol_3(driver):
    
    username_input = driver.find_element(By.ID, 'session_key')
    password_input = driver.find_element(By.ID, 'session_password')
    login_button = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/div/form/div[2]/button')
    logger.info("Found log in field on pop up🍾")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    logger.info('Keys sent to form🔑')
    login_button.click()
    time.sleep(1)

    return driver


def go_to_profile(driver):
    try:
        profile_picture = driver.find_element(By.XPATH, '//*[@id="ember164"]')
    except:
        try:
            profile_picture = driver.find_element(By.ID, 'ember463')
        except:
            logger.warning('I CANT CLICK😩🤯')
            try:
                profile_picture = driver.find_element(By.CLASS_NAME, 't-16 t-black t-bold')
            except:
                logger.error("R.I.P.💀💔 ")

    profile_picture.click()
    time.sleep(2)
    return driver


def get_experience(driver):

    section = driver.find_element(By.CLASS_NAME, 'pvs-list__outer-container')
    logger.info('Found correct section🔬')
    child_elements = section.find_elements(By.XPATH, './*')
    logger.info(f"Going to list all children of {section}")
    for child in child_elements:
        print(child.text)
    print('--all elements above--')
    return driver


def main():
    driver = webdriver.Chrome()
    driver.get(URL)
    try:
        driver = log_in_vol_1(driver)
    except:
        logger.warning('Could not find "email-or-phone" or "password"')
    
        try:
            driver = log_in_vol_2(driver)
        except:
            logger.warning('Could not log in with XPATHS')
            try:
                driver = log_in_vol_3(driver)
            except:
                logger.warning('Could not find IDs session_key session_password')
                driver.close()
                sys.exit()
    

    # logger.info(f'ACTION 2: --- find a user with search')
    # try:
    #     driver = find_user(driver, "stefan borek")
    # except:
    #     logger.info('Failed to perform a user search😢')


    driver.get(USER_URL)
    time.sleep(3)
    try:
        driver = get_experience(driver)
    except:
        logger.info('Failed to retrieve experience')

    page_source = driver.page_source

    from bs4 import BeautifulSoup

    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Now you can find elements by tag, class, id, etc.
    # For example, to find all the paragraphs you can use:
    paragraphs = soup.find_all('main')

    for paragraph in paragraphs:
        print(paragraph.text)

    driver.close()



if __name__ == "__main__":
    main()