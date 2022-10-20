'''
web_utilities.py

Common utilities used for accessing state websites.
'''

import os
import requests
import shutil
import time
import uuid
from constants import ROOT_DIRECTORY, SCREENSHOT_DIRECTORY
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from typing import Dict, List


def launch_chrome_browser(
    url: str,
    check_string,
    page_load_wait_in_sec=10,
    avoid_detection=False) -> WebDriver:
    '''
    Launches webdriver for a given url.

    Input: 
     - url (string)
     - check_string (string) check to ensure we went to the correct webpage

    Returns: selenium webdriver instance
    '''
    # Initialize default options for headless Chrome WebDriver
    chromeOptions = webdriver.ChromeOptions() 
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--disable-dev-shm-usage") 
    chromeOptions.add_argument("--hide-scrollbars")
    
    # Add additional options and run script if should avoid Selenium detection
    if avoid_detection:
        chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
        chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
        chromeOptions.add_experimental_option('useAutomationExtension', False)

        browser = webdriver.Chrome(options=chromeOptions)
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    else:
        browser = webdriver.Chrome(options=chromeOptions)
    
    # Navigate to page and confirm it's correct
    browser.get(url)
    time.sleep(page_load_wait_in_sec)
    assert check_string in browser.title

    # Wait one second for page to load
    return browser


def take_screenshot(browser: WebDriver, filename: str) -> None:
    '''
    Take a screenshot of current browser state.

    Inputs:
    - browser: (selenium webdriver instance)
    - filename: (string) of jpeg to be saved.
    '''
    # Adjust window size to capture full page
    time.sleep(3)
    required_width = browser.execute_script('return document.scrollingElement.scrollWidth')
    required_height = browser.execute_script('return document.scrollingElement.scrollHeight')
    browser.set_window_size(required_width, required_height)

    # Take screenshot
    os.makedirs(SCREENSHOT_DIRECTORY, exist_ok=True)
    browser.save_screenshot(f"{SCREENSHOT_DIRECTORY}/{filename}")


def complete_text_fields_id(text_elements: Dict, browser: WebDriver) -> None:
    '''
    Completes all text fields set up in dictionary by HTML object ID.

    Inputs: 
    - text_elements: (dictionary) with keys as html element ids (e.g., "city") 
      and values as (string) inputs, e.g., ("Miami")
    - browser: (selenium webdriver instance)
    '''
    for id, val in text_elements.items():
        elem = browser.find_element_by_id(id)
        elem.clear()
        elem.send_keys(val)
        elem.send_keys(Keys.TAB)
        time.sleep(0.5)


def complete_text_fields_name(text_elements: Dict, browser: WebDriver) -> None:
    '''
    Completes all text fields set up in dictionary by HTML object Name.
    Inputs: 
    - dictionary with keys as html element names (e.g., "city") and values as 
      string inputs, e.g., ("Miami")
    - current selenium webdriver instance (browser)
    '''
    for name, val in text_elements.items():
        var_ = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, name)))
        var_.send_keys(val)
        var_.send_keys(Keys.TAB)
        time.sleep(0.5)


def upload_photos(
    browser: WebDriver,
    image_urls: List[str],
    input_xpath: str,
    upload_wait_in_sec: int=10) -> None:
    '''
    Downloads images from URLs and then uploads
    each image to a webpage.

    Parameters:
        browser (WebDriver): A browser currently on
            the webpage of interest.

        image_urls (list of str): A list of image URLs.

        input_xpath (str): The xpath to the HTML file
            input element on the webpage.

        upload_wait_in_sec (int): The number of seconds
            to wait for the upload to complete before
            removing the downloaded images from the local
            file system. Defaults to 10.

    Returns:
        None
    '''
    # Create temp directory on file system
    unique_id = uuid.uuid4().hex
    photo_dir = f"{ROOT_DIRECTORY}/submissions/{unique_id}"
    os.makedirs(photo_dir, exist_ok=True)

    # Retrieve photos and write to temp directory as JPGs
    photo_paths = []
    for i in range(len(image_urls)):
        url = image_urls[i]
        response = requests.get(url)
        if not response.ok:
            raise Exception("Failed to retrieve FrackTracker "
                f"photo from '{url}'.")

        temp_file_name = f"{photo_dir}/photo_{i+1}.jpg"
        with open(temp_file_name, "wb") as f:
            f.write(response.content)
            photo_paths.append(os.path.abspath(temp_file_name))

    # Join photo file paths into one string and submit through input element
    # NOTE: Multiple files can be sent in one command
    photo_keys = '\n'.join(photo_paths)
    photo_input_elem = (WebDriverWait(browser, 20)
        .until(EC.presence_of_element_located((By.XPATH, input_xpath))))
    photo_input_elem.send_keys(photo_keys)

    # Wait for upload to complete and then remove temp directory
    time.sleep(upload_wait_in_sec)
    shutil.rmtree(photo_dir)


def submit_web_form(
    report_state: str,
    report_id: str,
    browser: WebDriver,
    find_by_method: str,
    find_by_target: str,
    submission_wait_in_seconds: int=10,
    confirmation_find_by_method=None,
    confirmation_find_by_target=None) -> None:
    '''
    Submits a web form and then takes a screenshot of the final page.

    References:
        - https://selenium-python.readthedocs.io/locating-elements.html

    Parameters:
        report_state (str): The name of the state associated
            with the webform (e.g., "Ohio").

        report_id (str): The id of the report to be submitted.
            Comes from the FracTracker API.

        browser (WebDriver): A browser currently on
            the webpage of interest.

        find_by_method (str): The method to use to retrieve
            the submit button (e.g., 'By.XPATH' for 'xpath').

        find_by_target (str): The target value of the
            `find_by_method`.

        submission_wait_in_seconds (int): The number of seconds
            to wait for the submission confirmation page to load.
            Defaults to 10.

        confirmation_find_by_method (str): The method to use to
            retrieve the confirmation button (e.g., 'By.XPATH' 
            for 'xpath').

        confirmation_find_by_target (str): The target value of the
            `confirmation_find_by_method`.

    Returns:
        None
    '''
    # Take screenshot of pre-submission screen
    path_prefix = f"{report_state.lower()}_{report_id}"
    image_path = f"{path_prefix}_pre_submission.png"
    take_screenshot(browser, image_path)

    # Click submit button and wait for next page to load
    submit_btn = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((find_by_method, find_by_target)))
    submit_btn.click()
    time.sleep(submission_wait_in_seconds)

    # Determine whether submission confirmation required
    if confirmation_find_by_method and confirmation_find_by_target:

        # Take screenshot of confirmation window
        image_path = f"{path_prefix}_confirmation.png"
        take_screenshot(browser, image_path)

        # Click confirmation button
        confirm_btn_lookup = (confirmation_find_by_method, confirmation_find_by_target)
        confirm_btn = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable(confirm_btn_lookup))
        confirm_btn.click()
        time.sleep(submission_wait_in_seconds)

    # Take screenshot of post-submission page
    image_path = f"{path_prefix}_post_submission.png"
    take_screenshot(browser, image_path)

    # Verify that page has changed by looking for existence of submit button
    try:
        submit_btn = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((find_by_method, find_by_target)))
    except TimeoutException:
        return

    raise Exception("Failed to click submit button "
        f"for {report_state} state report {report_id}.")
