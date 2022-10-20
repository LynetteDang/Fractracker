'''
new_mexico.py

Completes and submits the New Mexico Environment
Department's web form for complaints.
'''

import time
from constants import PROD, PROD_ENV, TEST
from models.base_report import Report
from models.metadata import WEB_SUBMISSION, Metadata, submit_and_return_metadata
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from typing import List
from utilities import web_utilities


AGENCY_NAME = "New Mexico Environment Department"
URL = "https://ents.web.env.nm.gov/public/INCIDENT_HDR_add.php"


def submit(report):
    '''
    Using information from report class, fill the webform with the relevant info

    Inputs:
        URL (string): the URL of the website
        Report (class instance): the information from the report class
    Outputs:
        screenshot (png): temporary output
    '''
    # Start browser instance
    browser = web_utilities.launch_chrome_browser(
        url=URL,
        check_string="Envir",
        avoid_detection=True)

    # Complaint Type
    # Directions say to select "No Match in List, Describe Below"
    select = Select(browser.find_element_by_name('value1'))
    select.select_by_value("ZZ")

    # County
    county = report.location.county.replace(' County', '')
    select = Select(browser.find_element_by_name('value13'))
    select.select_by_visible_text(county)

    # Text elements
    location = "The latitude-longitude is (" + format(report.lat) + "," + format(report.lon)+ ")"
    text_elements = {
        'value16': report.description,
        'value4': location,
        'value17': f'{report.first_name} {report.last_name}',
        'value24': report.email
    }
    complete_text_fields(text_elements, browser)

    # Submit and document new page in non-dev environments
    if PROD_ENV in [TEST, PROD]:
        submit_web_form(report.id, browser)

    # Quit browser instance
    browser.quit()


def complete_text_fields(text_elements, browser):
    '''
    Completes all text fields set up in dictionary.
    Inputs:
    - dictionary with keys as html element ids (e.g., "city") and values as
      string inputs, e.g., ("Miami")
    - current selenium webdriver instance (browser)
    '''
    for ids, val in text_elements.items():
        elem = browser.find_element_by_name(ids)
        elem.clear()
        elem.send_keys(val)
        elem.send_keys(Keys.TAB)
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
    path_prefix = f"new_mexico_{report_id}"
    image_path = f"{path_prefix}_pre_submission.png"
    web_utilities.take_screenshot(browser, image_path)

    # Click submit button and wait for next page to load
    submit_btn_lookup = (By.ID, "submit1")
    submit_btn = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(submit_btn_lookup))
    submit_btn.click()
    time.sleep(submission_wait_in_seconds)

    # Take screenshot of post-submission page
    image_path = f"{path_prefix}_post_submission.png"
    web_utilities.take_screenshot(browser, image_path)

    # Verify that page has changed by looking at whether the
    # HTML body text contains a success message
    body = browser.find_element_by_tag_name('body')
    body_text = body.get_attribute('innerHTML')
    if 'Your notification has been received.' not in body_text:
        raise Exception("Failed to click submit button "
            f"for New Mexico state report {report_id}.")


def main(report:Report) -> List[Metadata]:
    '''
    Creates final metadata for submissions.

    Parameters:
        report (Report instance): Single complaint from FracTracker API.
        
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
        state_name = 'New Mexico'
        logger.info(f"Creating mock report for {state_name}.")
        reports = get_mock_reports()
        nm_report = [r for r in reports if r.location.state.lower() == state_name.lower()][0]
    except IndexError:
        logger.info(f"No mock data for '{state_name}' has been configured.")
        exit(1)
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

    # Submit web form
    try:
        logger.info("Submitting web form.")
        metadata = main(nm_report)
        logger.info(metadata[0])
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)
