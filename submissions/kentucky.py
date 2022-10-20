'''
kentucky.py

Emails the Kentucky Energy and Environment Cabinet
with environmental complaints.
'''

from models.state_email import StateEmail
from models.base_report import Report
from models.metadata import EMAIL_SUBMISSION, Metadata, submit_and_return_metadata
from typing import List
from utilities.config import Config
from utilities.fractracker_api import FracAPI

AGENCY_NAME = "Kentucky Energy and Environment"
SUBJECT = "Environmental Complaint"


def submit(report:Report):
    '''
    Main function to send environmental complaint email to Kentucky state agency
    
    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    config = Config()
    kentucky_email = StateEmail(
        report=report,
        to_email=config.kentucky_email,
        from_email=config.from_email,
        cc_email=config.cc_email,
        agency=AGENCY_NAME,
        subject=SUBJECT
    )
    kentucky_email.email_agency()


def main(report: Report) -> List[Metadata]:
    '''
    Submits and returns metadata for a given report.

    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    email_metadata = submit_and_return_metadata(
        report=report,
        submit_fun=submit,
        submission_type=EMAIL_SUBMISSION,
        agency=AGENCY_NAME
    )
    return [email_metadata]


if __name__ == '__main__':
    api_results = FracAPI(begin_date="06-09-2019",
                          end_date="06-11-2019", check_emails=False)
    report = next(
        (x for x in api_results.reports if x.location.state == "Kentucky"), None)
    if report:
        print(report)
        main(report)
