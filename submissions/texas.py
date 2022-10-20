'''
texas.py

Completes and submits the Texas Comission on
Environmental Quality's web form for complaints.
'''

from constants import PROD, PROD_ENV, TEST
from datetime import datetime
from models.base_report import Report
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from typing import List
from utilities import web_utilities
from models.metadata import WEB_SUBMISSION, Metadata, submit_and_return_metadata
from utilities.logger import logger


AGENCY_NAME = "Texas Comission on Environmental Quality"
URL = "https://www.tceq.texas.gov/assets/public/compliance/monops/complaints/complaints.html"


def complete_all_fields(report: Report, browser: WebDriver):
    '''
    Completes web form for a specific report

    Parameters:
        report (Report instance): Single complaint from FracTracker API
        browser: (selenium webdriver instance)
    '''
    # Parse datetime
    report_date: datetime = datetime.fromisoformat(report.date)

    # All text elements
    text_elements = {
        'datepicker': report_date.strftime('%m/%d/%Y'),
        'location': report.location.full_address,
        'concern': report.description if report.description else "N/A",
        'name': f'{report.first_name} {report.last_name}',
        'email': report.email,
        'city': 'See address above',
        'who': 'N/A'
    }
    web_utilities.complete_text_fields_id(text_elements, browser)

    # Time observed in nearest 15-minute increment
    hour = 12 if report_date.hour in (0, 12) else report_date.hour % 12
    hour_str = str(hour)
    minute = round(report_date.minute / 15) * 15
    minute_str = str(minute).rjust(2, '0')
    time_observed = f"{hour_str}:{minute_str}"
    
    time_select = Select(browser.find_element_by_id('time'))
    time_select.select_by_value(time_observed)

    # AM or PM
    am_pm = 'am' if report_date.hour < 12 else 'pm'
    am_pm_select = Select(browser.find_element_by_id('ampm'))
    am_pm_select.select_by_value(am_pm)

    # County
    county = report.location.county.replace(' County', '').strip()
    county_select = Select(browser.find_element_by_id('county'))
    county_select.select_by_value(county)


def submit(report: Report):
    '''
    Main function to open headless chrome browswer and submit a state web form.

    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    # Extract report here to eliminate other code changes
    browser = web_utilities.launch_chrome_browser(
        url=URL,
        check_string="TCEQ",
        page_load_wait_in_sec=20,
        avoid_detection=True)

    complete_all_fields(report, browser)
    web_utilities.take_screenshot(browser, "texas.png")

    # Submit and document new page in non-dev environments
    if PROD_ENV in [TEST, PROD]:
        web_utilities.submit_web_form(
            report_state='texas',
            report_id=report.id,
            browser=browser,
            find_by_method=By.XPATH,
            find_by_target='//*[@id="content"]/p/button'
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
        state_name = 'Texas'
        logger.info(f"Creating mock report for {state_name}.")
        reports = get_mock_reports()
        tx_report = [r for r in reports if r.location.state.lower() == state_name.lower()][0]
    except IndexError:
        logger.info(f"No mock data for '{state_name}' has been configured.")
        exit(1)
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

    # Submit web form
    try:
        logger.info("Submitting web form.")
        metadata = main(tx_report)
        logger.info(metadata[0])
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)
