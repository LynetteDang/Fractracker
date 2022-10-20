'''
metadata.py

Class to store metadata from submission.
'''

from datetime import datetime
from types import FunctionType
from models.api_report import Report


WEB_SUBMISSION = 'web'
EMAIL_SUBMISSION = 'email'
STATUS_NOT_SUBMITTED = 'not submitted'
STATUS_SUBMITTED = 'submitted'
NA = 'N/A'


class Metadata:
    '''
    Class to store submission-related metadata
    '''
    def __init__(
        self,
        report:Report,
        submission_type:str=NA,
        agency:str=NA,
        status:str=STATUS_NOT_SUBMITTED,
        status_reason:str=NA,
        submission_time: datetime=NA):
        '''
        Constructor for Metadata class.
        
        Parameters:
            report (Report): instance of Report class.
            submission_type (str): "web" or "email"
            agency (str): Name of state agency (e.g., Colorado DEP)
            status (str): "Submitted" or "Not Submitted"
            status_reason (str): Reason for no submission

        Returns:
            None.  Updates attributes of class.
        '''
        self.id = report.id
        self.report_date = report.date
        self.agency = agency
        self.submission_type = submission_type
        self.status = status
        self.status_reason = status_reason
        self.submission_time = submission_time
        
        if report.location.is_valid:
            self.state = report.location.state
            self.county = report.location.county
        else:
            self.county, self.state = None, None

    
    def __str__(self):
        return f'{vars(self)}'


def submit_and_return_metadata(
    report:Report,
    submit_fun:FunctionType, 
    submission_type:str,
    agency:str) -> Metadata:
    '''
    Submits report to state agencies and prepares metadata.

    Parameters:
        report (Report instance): Single complaint from FracTracker API
        submit_fun (function): state-specific submission function
        submission_type (str): "web" or "email"
        agency (str): Name of state agency (e.g., Colorado DEP)
    Returns:
        Metadata instance corresponding to unqiue agency submissions.  
    '''
    try:
        submit_fun(report)
        return Metadata(
            report,
            submission_type=submission_type, 
            agency=agency, 
            status=STATUS_SUBMITTED,
            status_reason=None,
            submission_time=datetime.utcnow()
        )
    except Exception as e:
        return Metadata(
            report,
            submission_type=submission_type, 
            agency=agency,
            status=STATUS_NOT_SUBMITTED,
            status_reason=f"Error in submitting web form. {e}",
            submission_time=None
        )
