'''
colorado.py

Emails the Colorado Oil and Gas Conservation Commission
with environmental complaints. In addition, submits
complaints through the City and County of Broomfield,
Colorado's webform if the complaint occurs in that locale.
'''

from constants import DEV, PROD, PROD_ENV, TEST
from models.base_report import Report
from models.metadata import EMAIL_SUBMISSION, STATUS_SUBMITTED, NA, submit_and_return_metadata, Metadata
from models.state_email import StateEmail
from selenium.webdriver.support.ui import Select
from typing import List
from utilities import web_utilities
from utilities.config import Config
from utilities.fractracker_api import FracAPI


AGENCY_NAME = "Colorado Oil and Gas Conservation Commission"
SUBJECT = "Environmental Complaint"
URL = "https://dnrlaserfiche.state.co.us/Forms/ogcccomplaintnewintake"
MAX_ALLOWED_PHOTOS = 3


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
    driver = web_utilities.launch_chrome_browser(URL, "Submission")

    # Complaint Type - default value is others, and put specific value in input
    driver.find_element_by_id("Field103_other").click()
    text_elements_complaint_type = {'Field103_other_value': report.report_type}
    web_utilities.complete_text_fields_id(text_elements_complaint_type, driver)

    # County
    select = Select(driver.find_element_by_name('Field100'))
    select.select_by_visible_text(report.location.county)

    # connection to incident: choose other
    driver.find_element_by_id('Field95_other').click()
    # fill in other with NA value
    text_element_connection_incident = {'Field95_other_value': NA}
    web_utilities.complete_text_fields_id(text_element_connection_incident, driver)

    # will you provide personal information for this complaint, check yes
    driver.find_element_by_id('Field47-0').click()
    text_elements_personal_info = {
        'Field4': NA,
        'Field5': report.location.city,
        'Field45': report.first_name,
        'Field102': report.last_name,
        'Field7': report.location.zip,
        'Field8': report.email
    }
    web_utilities.complete_text_fields_id(text_elements_personal_info, driver)
    # best way to communicate is email
    driver.find_element_by_id('Field97-1').click()

    # description of complaint
    text_elements_description = {'Field50': report.location.full_address,
    'Field51': report.description}
    web_utilities.complete_text_fields_id(text_elements_description, driver)

    # Is this an ongoing issue(s)? check no
    driver.find_element_by_id('Field104-1').click()

    # Do you know who the oil and gas company is? check no
    driver.find_element_by_id('Field54-1').click()

    # attachment
    # Upload photos if there is attachment
    if report.image_url:
        driver.find_element_by_id('Field39-0').click()
        image_urls = report.image_url[:MAX_ALLOWED_PHOTOS]
        photo_xpath = "//input[@id='Field40']"
        web_utilities.upload_photos(driver, image_urls, photo_xpath)
    # if there is no attachment, check no
    else:
        driver.find_element_by_id('Field39-1').click()

    # Submit
    #driver.find_element_by_id('action').click()
    if PROD_ENV == TEST or PROD_ENV == DEV:
        image_path = f"{report.location.state}_{report.id}.png"
        web_utilities.take_screenshot(driver, image_path)

    elif PROD_ENV == PROD:
        submit_path = "action"
        web_utilities.submit_and_check(browser=driver,
                                       submit_string=submit_path, 
                                       id=True)

    # Quit browser instance
    driver.quit()


def main(report: Report) -> List[Metadata]:
    '''
    Main function to open headless chrome browser and submit a state web
    form and/or send environmental complaint email to Colorado state agency
    depending on report county
    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    config = Config()
    colorado_email = StateEmail(
        report=report,
        to_email=config.colorado_email,
        from_email=config.from_email,
        cc_email=config.cc_email,
        agency=AGENCY_NAME,
        subject=SUBJECT
    )
    colorado_email.email_agency()
    email_metadata = submit_and_return_metadata(
        report=report,
        submit_fun=StateEmail.email_agency,
        submission_type=EMAIL_SUBMISSION,
        agency=AGENCY_NAME
    )
    return [email_metadata]


if __name__ == '__main__':
    api_results = FracAPI(begin_date="12-02-2018",
                          end_date="12-02-2018", check_emails=False)
    report = next(
        (x for x in api_results.reports if x.location.state == "Colorado"), None)
    if report:
        data = Metadata(report, EMAIL_SUBMISSION,
                        AGENCY_NAME, STATUS_SUBMITTED, NA, NA)
        main(report)
