'''
submission.py

Utilities to process submissions to state agencies

'''

import pandas as pd
from models.base_report import Report
from models.metadata import Metadata
from submissions import *
from typing import List
from utilities.logger import logger


class Submission:
    '''
    Represents a complaint submission to a governmental agency.
    '''

    def __init__(self, report: Report) -> None:
        '''
        The constructor for `Submission`.

        Parameters: 
            report (Report): The report to submit.

        Returns:
            None
        '''
        self.report = report
        if not report.location.is_valid:
            self.metadata = [Metadata(report, status_reason='Location data invalid.')]
        else:
            self.metadata = self._submit_to_agency()
        

    def _submit_to_agency(self) -> List[pd.DataFrame]:
        '''
        If there are no errors with submission, send
        information to state via webform or email.

        Parameters:
            None

        Returns:
            (list of pd.DataFrame): The submission metadata.
        '''        
        try:
            # Replace spaces with underscores for states like "West Virginia"
            state_string = self.report.location.state.replace(' ', '_').lower()

            # Get reference to state Python module and call its
            # main method to submit complaint to state agenc(y/ies)
            fun = globals()[state_string]
            metadata = fun.main(self.report)

            # Log metadata from submission
            for meta in metadata:
                logger.info(f'Submitted report {meta.id} to '
                    f'{meta.agency} via {meta.submission_type}')

            return metadata

        except KeyError:
            msg = 'State not yet configured for submission.'
            return [Metadata(self.report, status_reason = msg)]        

