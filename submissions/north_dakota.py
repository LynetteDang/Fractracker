'''
north_dakota.py

Emails North Dakota Department of Environmental Quality
with environmental complaints.
'''

from models.base_report import Report
from models.metadata import EMAIL_SUBMISSION, submit_and_return_metadata
from models.state_email import StateEmail
from utilities.config import Config
from utilities.fractracker_api import FracAPI


AGENCY_NAME = "North Dakota Department of Environmental Quality"
SUBJECT = "Environmental Complaint"


def main(report: Report):
    '''
    Main function to send environmental complaint email to North Dakota state agency
    Parameters:
        report (Report instance): Single complaint from FracTracker API
    '''
    config = Config()
    north_dakota_email = StateEmail(
        report=report,
        to_email=config.north_dakota_email,
        from_email=config.from_email,
        cc_email=config.cc_email,
        agency=AGENCY_NAME,
        subject=SUBJECT
    )
    north_dakota_email.email_agency()
    email_metadata = submit_and_return_metadata(
        report=report,
        submit_fun=StateEmail.email_agency,
        submission_type=EMAIL_SUBMISSION,
        agency=AGENCY_NAME
    )
    return [email_metadata]


if __name__ == '__main__':
    api_results = FracAPI(begin_date="05-08-2018",
                          end_date="05-12-2018", check_emails=False)
    report = next(
        (x for x in api_results.reports if x.location.state == "North Dakota"), None)
    if report:
        print(report)
        main(report)
