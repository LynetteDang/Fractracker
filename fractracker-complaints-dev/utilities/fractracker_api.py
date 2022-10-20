'''
fractracker_api.py

Utilities for interfacing with FracTracker Alliance's internal APIs.
'''

import datetime
import os
import requests
from datetime import datetime
from models.api_report import ApiReport
from typing import Dict, List
from utilities.logger import logger

FRACTRACKER_BASE_ENDPOINT = "https://api.fractracker.org/v1/data/report"
class FracAPI:
    '''
    Class to store results from Fractracker API query.
    '''

    def __init__(
        self, 
        begin_date:str, 
        end_date:str=None,
        check_emails:bool=True) -> None:
        '''
        Constructor for FracAPI class.
        
        Parameters:
            begin_date (str): The inclusive minimum report date.
                Formatted as "MM-DD-YYYY".

            end_date (str): The inclusive maximum report date.
                Formatted as "MM-DD-YYYY". If no value provided,
                defaults to current date.
            
            check_emails (bool): A boolean indicating whether
                report email addresses should be validated.

        Returns:
            None
        '''
        # Parse start and end dates
        today = datetime.now()
        date_fmt = "%m-%d-%Y"
        self.begin_date = datetime.strptime(begin_date, date_fmt)
        if type(end_date) == str:
            self.end_date = datetime.strptime(end_date, date_fmt)
        else:
            self.end_date = today

        # Confirm we have correct dates that precede today
        assert self.begin_date <= today and self.end_date <= today

        self.query = self.gen_query()

        # Get all reports and then remove duplicates
        self.reports = self.get_reports_for_date(check_emails)

    def gen_query(self) -> List[str]:
        '''
        Creates query filter for a date range.

        Parameters:
            None

        Returns:
            (list of str): The list of filter strings.
        '''
        begin_date_filter = self.gen_date_filter(self.begin_date, "ge")
        end_date_filter = self.gen_date_filter(self.end_date, "le")
        return [f'{{"filters":[{begin_date_filter},{end_date_filter}]}}']

    def gen_date_filter(self, date:datetime, operator:str) -> str:
        '''
        Helper function to convert datetime to a line in API query filter.

        Parameters:
            date (datetime): The date to filter by.

            operator (str): The comparison operator to use when filtering.

        Returns:
            (str): The filter string.
        '''
        str_date = date.isoformat()
        return f'{{"val": "{str_date}","op":"{operator}","name":"report_date"}}'

    def get_one_page(self, page_num:int=1) -> List[Dict]:
        '''
        Accesses the FracTracker API for a single
        page of json-formatted reports. 
        
        Inputs:
            page_num (int): The page of reports to retrieve.
                Defaults to one.

        Returns:
            (list of dict): JSON-structured response containing reports.
        '''
        params = {'q': self.query, 'page': page_num}
        response = requests.get(FRACTRACKER_BASE_ENDPOINT, params=params)

        if not response.ok:
            raise Exception(f"Call for reports failed with status code "
                f"'{response.status_code} - {response.reason}'.")
        
        return response.json()

    def process_current_page(
        self,
        new_page: Dict,
        reports: List[ApiReport], 
        check_emails: bool) -> List[ApiReport]:
        '''
        Takes a new json page and adds new reports to list of Reports. Handles 
        duplicate reports by adding new images to a list of image_urls in 
        the existing report within report list.

        Inputs:
            new_page: (dict) json returned for one page of an API call.
            
            reports: (list of Report instances) list of current reports
            
            check_emails (bool): A boolean indicating whether
                report email addresses should be validated.
            
        Returns:
            reports: (list of Report instances) list of updated reports
        '''
        for r in new_page['features']:
            new_report = ApiReport(r, check_emails)
            add_report = True
            for i, old_report in enumerate(reports):
                if new_report == old_report:
                    # Add new image to other report and replace
                    old_report.image_url.extend(new_report.image_url)
                    reports[i] = old_report
                    add_report = False
                    break # stop at first duplicate
            if add_report:
                reports.append(new_report)
        return reports

    def get_reports_for_date(self, check_emails:bool) -> List[ApiReport]:
        '''
        Queries API for all reports by looping over all pages.
        
        Inputs:
            check_emails (bool): A boolean indicating whether
                report email addresses should be validated.

        Returns:
            (list of reports): The retrieved reports.
        '''
        first_page_json = self.get_one_page()
        num_pages = first_page_json['properties']['total_pages']
        num_results = first_page_json['properties']['num_results']
        
        logger.info(f'Total number of pages: {num_pages}')
        logger.info(f'Total number of reports: {num_results}')     

        # Initialize feature list as first page list
        reports = []
        for page_num in range(num_pages):
            new_page = self.get_one_page(page_num=page_num + 1)
            new_reports = [ApiReport(r, check_emails) for r in new_page['features']]
            reports.extend(new_reports)
            logger.info(f'Processed page {page_num+1}/{num_pages}')

        return reports
