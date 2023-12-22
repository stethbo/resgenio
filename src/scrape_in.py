import os
import sys
import re
import logging
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from app.models import db, LinkedinData

logger = logging.getLogger(__file__)


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


def get_page_source(user_url: str):
    options = Options()
    # options.add_argument("--headless=new")
    logger.info(options)
    driver = webdriver.Firefox() #options=options)
    driver.get(URL) # going to LinkedIn.com
    try:
        driver = log_in_vol_1(driver)
    except:
        logger.warning('Could not find "email-or-phone" or "password"')
        try:
            driver = log_in_vol_2(driver)
        except:
            logger.warning('Could not log in with XPATHS')
            sys.exit()

    driver.get(user_url)
    time.sleep(2)

    try:
        page_source = driver.page_source
        logger.info(f"Got page source of type: {type(page_source)}")
    except Exception as e:
        page_source = None
        logger.error(f'Failed to get the page source :/')
        logger.error(f'Got execption: {e}')
    
    driver.close()

    return page_source


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


def cut_key_paragraphs(page_content: str) -> str:
    user_info = ''
    user_info += 'Experience:\n' + get_section(page_content, 'Experience', 'Education')
    user_info += '\nEducation\n' + get_section(page_content, 'Education', 'Licenses & certifications')
    user_info += '\nCertifications\n' + get_section(page_content, 'Licenses & certifications', 'Skills\n')
    return user_info


def generate_page_paragraphs(profile_url: str):
    page_source = get_page_source(user_url=profile_url)
    soup = BeautifulSoup(page_source, 'html.parser')
    paragraphs = soup.find_all('span', class_='visually-hidden')
    logger.info(f'Found total of: {len(paragraphs)} paragraphs.')

    page_content = ''
    for paragraph in paragraphs:
        line = paragraph.text
        line = re.sub(r'\s{2,}', '', line)
        line = re.sub(r'\n', '', line)
        if line != '':
            page_content += line + '\n'

    user_info = f'LinkedIn: {profile_url}\n\n' + cut_key_paragraphs(page_content)

    return user_info




def get_linkedin_data(user_url: str) -> str:
    user_id = re.sub(r'/$', '', user_url)  # deleting the / if exist at the end of a string
    user_id = user_id.split('/')[-1]  # getting the user ID from URL
    logger.info(f"Working on user ID: {user_id}")

    try:
        record = LinkedinData.query.filter_by(url=user_url).one()
        user_info = record.profile_data
    except NoResultFound:
        user_info = generate_page_paragraphs(profile_url=user_url)
        new_record = LinkedinData(url=user_url, profile_data=user_info, timestamp=datetime.now())
        db.session.add(new_record)
        db.session.commit()

    return user_info


def main():
    user_info = get_linkedin_data(USER_URL)
    print(f'Got following user info:\n {user_info}')
    logger.info('See you G🦍 ')

if __name__ == "__main__":
    main()