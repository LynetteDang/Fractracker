'''
pennsylvania.py

Completes and submits the Pennsylvania Department
of Environmental Protection's web form for complaints.
'''

import time
from typing import List
from constants import PROD, PROD_ENV, TEST
from models.base_report import Report
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utilities import web_utilities
from models.metadata import WEB_SUBMISSION, Metadata, submit_and_return_metadata


AGENCY_NAME = "Pennsylvania Department of Environmental Protection"
URL = "https://www.depgreenport.state.pa.us/EnvironmentalComplaintForm/"


def complete_all_fields(report: Report, browser: WebDriver):
    '''
    Completes all fields on web form

    Inputs:
        report (Instance of Report): single complaint from FracTracker API
        browser (Instance of Selenium webdriver): current chrome webdriver
    '''
    # Complete text elements
    location_entry = f'''Latitude: {report.lat} \
                         Longitude: {report.lon} \
                         Address: {report.location.full_address}'''
    text_elements = {"ec_name":f"{report.first_name} {report.last_name}",
                    "email": report.email,
                    "pd1_comments_field": report.description,
                    "pd2_comments_field": location_entry}
    web_utilities.complete_text_fields_id(text_elements, browser)

    # Configure email options
    browser.find_element_by_id("ConfirmationCheckYes").click()
    time.sleep(.5)

    # Agree to give valid email address
    browser.find_element_by_id("buttonOk").click()

    ## COMPLAINT INFO
    # County
    county = report.location.county.replace(' County', '')
    select = Select(browser.find_element_by_id('countyProblem'))
    select.select_by_visible_text(county)

    # Township
    address_chunks = report.location.full_address.split(", ")
    select = Select(browser.find_element_by_id('locationProblem'))
    for chunk in address_chunks:
        for option in select.options:
            if option.get_attribute("value") == chunk:
                option.click()
                break

    # Select "No, we don't know who is responsible"
    xpath = "//input[@type='radio' and @name='OBKey__312_1' and @value='0']"
    browser.find_element_by_xpath(xpath).click()


def submit(report:Report):
    '''
    Main function to open headless chrome browswer and submit a state web form.
    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    # Launch web browser
    browser = web_utilities.launch_chrome_browser(
        url=URL,
        check_string="Complaint Form",
        avoid_detection=True)

    # Populate fields
    complete_all_fields(report, browser)
    web_utilities.take_screenshot(browser, "pa.png")

    # Submit and document new page in non-dev environments
    if PROD_ENV in [TEST, PROD]:
        web_utilities.submit_web_form(
            report_state='pennsylvania',
            report_id=report.id,
            browser=browser,
            find_by_method=By.ID,
            find_by_target='SubmitButton',
            confirmation_find_by_method=By.ID,
            confirmation_find_by_target='submitForm'
        )

    # Quit browser instance
    browser.quit()


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
        state_name = 'Pennsylvania'
        logger.info(f"Creating mock report for {state_name}.")
        reports = get_mock_reports()
        pa_report = [r for r in reports if r.location.state.lower() == state_name.lower()][0]
    except IndexError:
        logger.info(f"No mock data for '{state_name}' has been configured.")
        exit(1)
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

    # Submit web form
    try:
        logger.info("Submitting web form.")
        metadata = main(pa_report)
        logger.info(metadata[0])
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)
