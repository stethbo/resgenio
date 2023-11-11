import os
import sys
import re
import logging
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()
URL = 'https://www.linkedin.com'
USER_URL = "https://www.linkedin.com/in/stefan-borek-662510236"
USERNAME = os.environ.get("IN_USERNAME")
PASSWORD = os.environ.get("IN_PASSWORD")
#TODO: add at least 1 extra account to switch en case failed log in🥷


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
    print("log in method 1")

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
    print("log in method 2")

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
    print("log in method 3")

    return driver


def get_page_source():
    driver = webdriver.Firefox()
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

    driver.get(USER_URL)
    time.sleep(2)
    try:
        page_source = driver.page_source
        logger.info("Got page source")
    except Exception as e:
        page_source = None
        logger.error(f'Failed to get the page source :/')
        logger.error(f'Got execption: {e}')
    
    driver.close()

    return page_source

def generate_page_paragraphs(save_to: str):
    page_source = get_page_source()
    soup = BeautifulSoup(page_source, 'html.parser')
    with open('../data/whole_source.txt', 'w') as file_:
        file_.write(soup.text)

    paragraphs = soup.find_all('span', class_='visually-hidden')
    logger.info(f'Found total of: {len(paragraphs)} paragraphs.')
    with open(save_to, 'w') as txt_file:
        for paragraph in paragraphs:
            line = paragraph.text
            line = re.sub(r'\s{2,}', '', line)
            line = re.sub(r'\n', '', line)
            if line != '':
                txt_file.write(line + '\n')
                
        logger.info(f'Saved to file: {save_to}🥨')    


def get_first_match(text: str, pattern: re.compile) -> str:

    match = pattern.search(text)

    if match:
        content = match.group(1)
    else:
        content = '<Not found>'
        logger.info(f"No match found for patter: {pattern}")

    return content


def get_section(soup_text: BeautifulSoup.text, start_keyword: str, end_keyword: str):

    pattern = re.compile(rf'{start_keyword}(.*?){end_keyword}', re.DOTALL)

    return get_first_match(soup_text, pattern)


def get_user_info(user_url: str=USER_URL) -> str:
    user_id = USER_URL.split('/')[-1]
    logger.info(f"Working on user ID: {user_id}")
    paragraphs_file = os.path.join("..", "data", f"page_paragraphs_{user_id}.txt")

    if not os.path.exists(path=paragraphs_file):
        generate_page_paragraphs(paragraphs_file)
    
    page_content = open(paragraphs_file, 'r').read()
    
    user_info = ''
    user_info += 'Experience:\n' + get_section(page_content, 'Experience', 'Education')
    user_info += 'Education\n' + get_section(page_content, 'Education', 'Licenses & certifications')
    user_info += 'Certifications\n' + get_section(page_content, 'Licenses & certifications', 'Interests')

    return user_info

def main():
    user_info = get_user_info()
    print(f'Got following user info:\n {user_info}')
    logger.info('See you G🦍 ')

if __name__ == "__main__":
    main()