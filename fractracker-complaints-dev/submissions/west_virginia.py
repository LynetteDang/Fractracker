'''
west_virginia.py

Completes and submits the West Virginia Department
of Environmental Protection's web form for complaints
or emails a contact if the complaint is specifically
related to air quality.
'''

from constants import PROD, PROD_ENV, TEST
from models.base_report import Report
from models.metadata import EMAIL_SUBMISSION, WEB_SUBMISSION, Metadata, submit_and_return_metadata
from models.state_email import StateEmail
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from typing import List
from utilities import web_utilities
from utilities.config import Config


AGENCY_NAME = "West Virginia Department of Environmental Protection"
SUBJECT = "Environmental Complaint"
URL = "https://dep.wv.gov/WWE/ee/geninfo/Pages/complaints.aspx"


def submit_web_form(report: Report):
    '''
    Takes in a report instance and fills in the West Virginia website information.

    Inputs:
        URL (str): website URL - saved in .env
        Report (class instance): objects associated with specific report
    Output:
        screenshot: Temporary output
    '''
    # Launch web browser and switch to form contained in iframe
    browser = web_utilities.launch_chrome_browser(URL, "Complaint")
    browser.switch_to.frame("MSOPageViewerWebPart_WebPartWPQ1")

    # Select county
    selector = Select(browser.find_element_by_name('c_county'))
    county = report.location.county.replace(' County', '')
    selector.select_by_value(county)
    
    # Enter data into text fields
    text_elements = {
        'c_location': f"The latitude-longitude is ({report.lat}, {report.lon})",
        'c_description': report.description,
        'c_name': f'{report.first_name} {report.last_name}'
    }
    web_utilities.complete_text_fields_name(text_elements, browser)
    web_utilities.take_screenshot(browser, "wv.png")

    # Submit and document new page in non-dev environments
    if PROD_ENV in [TEST, PROD]:
        print("Submitting form.")
        web_utilities.submit_web_form(
            report_state='west_virginia',
            report_id=report.id,
            browser=browser,
            find_by_method=By.NAME,
            find_by_target='submit'
        )

    # Quit browser instance
    browser.quit()


def main(report:Report) -> List[Metadata]:
    '''
    Main function to open headless chrome browser and submit a state web
    form and/or send environmental complaint email to West Virginia state agency
    depending on report type

    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    if report.senses["Smell"] or report.report_type == "Compressors":
        config = Config()
        west_virginia_email = StateEmail(
            report=report,
            to_email=config.west_virginia_email,
            from_email=config.from_email,
            cc_email=config.cc_email,
            agency=AGENCY_NAME,
            subject=SUBJECT
        )
        west_virginia_email.email_agency()
        email_metadata = submit_and_return_metadata(
            report=report,
            submit_fun=StateEmail.email_agency,
            submission_type=EMAIL_SUBMISSION,
            agency=AGENCY_NAME
        )
        return [email_metadata]
    else:
        web_form_metadata = submit_and_return_metadata(
            report=report,
            submit_fun=submit_web_form,
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
        state_name = 'West Virginia'
        logger.info(f"Creating mock report for {state_name}.")
        reports = get_mock_reports()
        wv_report = [r for r in reports if r.location.state.lower() == state_name.lower()][0]
    except IndexError:
        logger.info(f"No mock data for '{state_name}' has been configured.")
        exit(1)
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

    # Submit web form
    try:
        logger.info("Submitting web form.")
        metadata = main(wv_report)
        logger.info(metadata[0])
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)
