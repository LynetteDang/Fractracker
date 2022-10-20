'''
california.py

Completes and submits the California EPA Environmental
Complaint System's web form for complaints.
'''

import time
from constants import PROD, TEST, PROD_ENV
from datetime import datetime
from models.base_report import Report
from models.metadata import WEB_SUBMISSION, Metadata, submit_and_return_metadata
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utilities import web_utilities


URL = "https://calepacomplaints.secure.force.com/complaints/"
AGENCY_NAME = "California EPA Environmental Complaint System"


def submit(report: Report):
    '''
    Fill the CA webform with relevant information from report

    Input: report (class instance)
    '''
    # Launch web browser
    browser = web_utilities.launch_chrome_browser(URL, "New")

    # PAGE 1

    # Populate complaint type field
    complaint = complaint_type(report)
    cat_comp = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, complaint)))
    cat_comp.click()
    time.sleep(0.5)

    # Take screenshot of page one
    path_prefix = f"california_{report.id}"
    web_utilities.take_screenshot(browser, f"{path_prefix}_pg1.png")
    
    # Click button to move to page two
    first_pg_submit = "//*[@id='complaintDetailsButton']"
    browser.find_element_by_xpath(first_pg_submit).click()

    # PAGE 2

    # Populate description and location text boxes
    loc = f"The latitude-longitude is ({report.lat}, {report.lon})."
    text_elements2 = {
        "details:JCMC:detailsForm:descriptionTextArea": report.description,
        "details:JCMC:detailsForm:locationDescriptionTextArea": loc
    }
    web_utilities.complete_text_fields_name(text_elements2, browser)

    # Populate date
    date_ = datetime.fromisoformat(report.date)
    month_ = date_.strftime("%b")
    year_ = date_.strftime("%Y")
    full_year = date_.strftime('%m/%d/%Y')

    first_click = "//*[@id='dateOfOccurence']/div/div/div[1]/div[1]/table/thead/tr[1]/th[2]"
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, first_click))).click()
    second_click = "//*[@id='dateOfOccurence']/div/div/div[1]/div[2]/table/thead/tr/th[2]"
    WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, second_click))).click()
    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[.='" +    year_ + "']"))).click()
    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[.='" + month_ + "']"))).click()
    WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td[data-day='" + full_year + "']"))).click()

    # Populate photos
    # image_urls = report.image_url[:1]
    # photo_xpath = "//*[@id='details:JCMC:detailsForm:fileInput']"
    # web_utilities.upload_photos(browser, image_urls, photo_xpath)
    # time.sleep(4)
    
    #Something here isn't working and causes the webpage to go blank
    #browser.find_element_by_css_selector("input[onclick*='attachmentStatus()']").click()

    #attach_xpath = "//*[@id='details:JCMC:detailsForm']/div[7]/div[3]/div/div[1]/div"
    # WebDriverWait(driver, 20).until(
    #         EC.element_to_be_clickable((By.ID, "details:JCMC:detailsForm:attachButton"))).click()
    #attach_elem = (WebDriverWait(driver, 20
       #).until(EC.presence_of_element_located((By.XPATH, attach_xpath)))).click()
    #attach_elem.click();

    time.sleep(10)

    # Take a screenshot of page two
    web_utilities.take_screenshot(browser, f"{path_prefix}_pg2.png")

    # Click button to move to page three
    second_pg_submit= "//*[@id='almostDoneButton']"
    browser.find_element_by_xpath(second_pg_submit).click()
    web_utilities.take_screenshot(browser, "_pg3.png")

    # PAGE THREE

    # Populate user fields
    text_elements = {
        "ComplaintContact:JCMC:AnonymousForm:FirstName":report.first_name,
        "ComplaintContact:JCMC:AnonymousForm:LastName":report.last_name,
        "ComplaintContact:JCMC:AnonymousForm:email": report.email,
        "ComplaintContact:JCMC:AnonymousForm:confirmEmail": report.email
    }
    web_utilities.complete_text_fields_name(text_elements, browser)

    # Take screenshot of page three
    web_utilities.take_screenshot(browser, f"{path_prefix}_pg3.png")

    # Submit and document new page in non-dev environments
    if PROD_ENV in [TEST, PROD]:
        web_utilities.submit_web_form(
            report_state='california',
            report_id=report.id,
            browser=browser,
            find_by_method=By.XPATH,
            find_by_target="//*[@id='iButton']"
        )

    # Quit browser instance
    browser.quit()


def complaint_type(report):
    '''
    Choose the complaint type based on different report options
    '''
    if report.senses["Taste"]:
        complaint_type = "//*[@id='water']"

    elif report.senses["Touch"] or ("Landfills" in report.report_type):
        complaint_type = "//*[@id='waste']"
    else:
        complaint_type = "//*[@id='air']"
        #toxic_substance = "//*[@id='toxic']"
        #pesticides = "//*[@id='pesticide']"
    return complaint_type


def main(report:Report) -> List[Metadata]:
    '''
    Creates final metadata for submissions.
    Parameters:
        report (Report instance): Single complaint from FracTracker API
    Returns:
        List of Metadata instances corresponding to unique agency submissions.
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
        state_name = 'California'
        logger.info(f"Creating mock report for {state_name}.")
        reports = get_mock_reports()
        ca_report = [r for r in reports if r.location.state.lower() == state_name.lower()][0]
    except IndexError:
        logger.info(f"No mock data for '{state_name}' has been configured.")
        exit(1)
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)

    # Submit web form
    try:
        logger.info("Submitting web form.")
        metadata = main(ca_report)
        logger.info(metadata[0])
    except Exception as e:
        logger.error(f"Submission for '{state_name}' failed. {e}")
        exit(1)
