'''
ohio.py
Completes and submits the Ohio Environmental
Protection Agency's web form for complaints.
'''

import time
from constants import PROD, PROD_ENV, TEST
from datetime import datetime
from models.base_report import Report
from models.metadata import WEB_SUBMISSION, Metadata
from models.metadata import submit_and_return_metadata
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Dict, List, Tuple
from utilities import web_utilities


AGENCY_NAME = "Ohio Environmental Protection Agency"
URL ="https://survey123.arcgis.com/share/af6b0b7597d842cb8debfc73c51ff085"
MAX_ALLOWED_PHOTOS = 3

def fill_dictionaries(report: Report) -> Tuple[Dict, Dict]:
    '''
    Fill the dictionaries with the relevant paths and information
    Input: Report (class instance)
    Output:
        dict_xpath (dict) - dictionary of the xpaths to each element
        dict_text (dict) - dictionary of the text information for each element
    '''
    dict_xpath = {
        'description': "//*[@id='Complaints']/label[1]/textarea",
        'latitude': "//label[@class='geo lat']",
        'longitude': "//label[@class='geo long']",
        'date': "//*[@id='Complaints']/label[5]/div/div[2]/input",
        'name': "//*[@id='Complaints']/section[2]/fieldset/label[1]/input",
        'email': "//*[@id='Complaints']/section[2]/fieldset/label[7]/input"
    }  

    dict_text = {
        'description': report.description,
        'latitude': str(report.lat),
        'longitude': str(report.lon),
        'date': datetime.fromisoformat(report.date).strftime('%m/%d/%Y'),
        'name': " ".join([report.first_name,report.last_name]),
        'email': report.email
    }
    return dict_xpath, dict_text


def submit(report: Report) -> None:
    '''
    Pushes and fills all necessary buttons to submit a claim for Ohio.
    Inputs:
        report - Class instance
        url (str) - the OH reporting website url
        dict_xpath (dict) - the xpaths for the dict keys
    '''
    # Launch browser
    browser = web_utilities.launch_chrome_browser(URL, "Environmental Complaint")
    
    # Fill in all the text variables
    complex_bypath(browser, report)

    # Populate complaint category
    complaint_cat = complaint_category(report)
    cat_comp = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, complaint_cat)))
    cat_comp.click()
    time.sleep(0.5)

    # Populate complaint type
    other = "//*[@id='Complaints']/fieldset[2]/fieldset/div/label[last()]"
    other_cat = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, other)))
    other_cat.click()
    time.sleep(0.5)

    # Upload photos
    if report.image_url:
        image_urls = report.image_url[:MAX_ALLOWED_PHOTOS]
        photo_xpath = '//*[@id="Complaints"]/label[6]/input[1]'
        web_utilities.upload_photos(browser, image_urls, photo_xpath)

    # Save tracking number
    complaint_tracking = browser.find_element_by_xpath("//*[@id='Complaints']/label[8]/p").text

    # Submit and document new page in non-dev environments
    if PROD_ENV in [TEST, PROD]:
        submit_web_form(report.id, browser)

    # Quit browser instance
    browser.quit()


def complaint_category(report: Report) -> str:
    '''
    Choosing and clicking the correct category for complaint
    Input:
        report (class instance) - the information received about a specific report
    Output:
        complaint_type (str) - the xpath needed for specific complaint category
    '''
    if report.senses["Taste"]:
        # drinking water
        complaint_type = "//*[@id='Complaints']/fieldset[1]/fieldset/div/label[3]"
    elif  report.senses["Smell"]:
        # air
        complaint_type = "//*[@id='Complaints']/fieldset[1]/fieldset/div/label[1]"
    elif report.senses["Sound"]:
        # land
        complaint_type = "//*[@id='Complaints']/fieldset[1]/fieldset/div/label[4]"
    elif any(c in ["Compressors", "Refineries"] for c in report.report_type):
        complaint_type = "//*[@id='Complaints']/fieldset[1]/fieldset/div/label[1]"
    elif any(c in ["Pits", "Mines"] for c in report.report_type):
        # water
        complaint_type = "//*[@id='Complaints']/fieldset[1]/fieldset/div/label[2]"
    else:
        complaint_type = "//*[@id='Complaints']/fieldset[1]/fieldset/div/label[4]"
    return complaint_type


def complex_bypath(browser: WebDriver, report: Report) -> None:
    '''
    Takes the text information from the report and fills in website form
    Inputs:
        browser - Current selenium webdriver instance
        report (class instance) - report class instance
    '''
    dict_xpath, dict_text = fill_dictionaries(report)
    for key, _ in dict_text.items():
        var_ = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, dict_xpath[key])))
        var_.send_keys(dict_text[key])
        if key != "date":
            var_.send_keys(Keys.TAB)
        time.sleep(0.5)


def submit_web_form(
    report_id: str,
    browser: WebDriver,
    submission_wait_in_seconds: int=10) -> None:
    '''
    Submits a web form and then takes a screenshot of the final page.

    References:
        - https://selenium-python.readthedocs.io/locating-elements.html

    Parameters:
        report_id (str): The id of the report to be submitted.
            Comes from the FracTracker API.

        browser (WebDriver): A browser currently on
            the webpage of interest.

        submission_wait_in_seconds (int): The number of seconds
            to wait for the submission confirmation page to load.
            Defaults to 10.

    Returns:
        None
    '''
    # Take screenshot of pre-submission screen
    path_prefix = f"ohio_{report_id}"
    image_path = f"{path_prefix}_pre_submission.png"
    web_utilities.take_screenshot(browser, image_path)

    # Click submit button and wait for next page to load
    submit_btn_lookup = (By.XPATH, "//*[@id='validate-form']")
    submit_btn = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(submit_btn_lookup))
    submit_btn.click()
    time.sleep(submission_wait_in_seconds)

    # Take screenshot of post-submission page
    image_path = f"{path_prefix}_post_submission.png"
    web_utilities.take_screenshot(browser, image_path)

    # Verify that page has changed by looking at whether the
    # submission success section no longer has a "hide" attribute.
    success_section = browser.find_element_by_id('screenContentPage')
    success_section_cls_attrs = success_section.get_attribute('class')
    if 'hide' in success_section_cls_attrs:
        raise Exception("Failed to click submit button "
            f"for Ohio state report {report_id}.")


def main(report:Report) -> List[Metadata]:
    '''
    Creates final metadata for submissions.
    Parameters:
        report (Report instance): Single complaint from FracTracker API
    Returns:
        List of Metadata instances corresponding to unqiue agency submissions. 
    '''
    web_form_metadata = submit_and_return_metadata(
        report=report,
        submit_fun=submit, 
        submission_type=WEB_SUBMISSION,
        agency=AGENCY_NAME
    )
    
    return [web_form_metadata]


if __name__ == "__main__":
    # Declare imports for testing
    from main import get_mock_reports
    from utilities.logger import logger

    # Generate mock reports
    try:
        state_name = 'Ohio'
        logger.info(f"Creating mock report for {state_name}.")
        reports = get_mock_reports()
        oh_report = [r for r in reports if r.location.state.lower() == state_name.lower()][0]
    except IndexError:
        logger.info(f"No mock data for '{state_name}' has been configured.")
        exit(1)
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

    # Submit web form
    try:
        logger.info("Submitting web form.")
        metadata = main(oh_report)
        logger.info(metadata[0])
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

