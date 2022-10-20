'''
mock_report.py
'''

import uuid
from datetime import datetime
from typing import Dict, List
from models.base_location import Location
from models.base_report import Report
from models.mock_location import MockLocation


class MockReport(Report):
    '''
    A mock report to use for test submissions.
    '''

    def __init__(self, json: Dict) -> None:
        '''
        The constructor for `MockReport`.

        Parameters:
            json (Dict): Properties needed to create
                the mock report and its associated
                location.

        Returns:
            None
        '''
        id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y_%m_%d")
        self._id = f"test_{timestamp}_{id}"
        self._lat = json['lat']
        self._lon = json['lon']
        self._location = MockLocation(
            lat=self._lat,
            lon=self._lon,
            state=json['state'],
            zip=json['zip'],
            county=json['county'],
            full_address=json['full_address']
        )


    @property
    def id(self) -> str:
        '''
        The report id.
        '''
        return self._id


    @property
    def lat(self) -> float:
        '''
        The latitude of the incident described by the report. 
        '''
        return self._lat


    @property
    def lon(self) -> float:
        '''
        The longitude of the incident described by the report. 
        '''
        return self._lon


    @property
    def description(self) -> str:
        '''
        The report description. 
        '''
        return 'PLEASE DISREGARD THIS SUBMISSION.'


    @property
    def date(self) -> str:
        '''
        The date on which the report was submitted. Uses ISO format.
        '''
        return '2018-01-02T22:08:12.510696'

    
    @property
    def first_name(self) -> str:
        '''
        The first name of the FracTracker user submitting the report. 
        '''
        return 'N/A'


    @property
    def last_name(self) -> str:
        '''
        The last name of the FracTracker user submitting the report. 
        '''
        return 'N/A'


    @property
    def email(self) -> str:
        '''
        The email address of the FracTracker user submitting the report. 
        '''
        return 'noreply@noreply.com'


    @property
    def location(self) -> Location:
        '''
        The location in which the user observed an incident. 
        '''
        return self._location


    @property
    def senses(self) -> Dict:
        '''
        A dictionary enumerating affected user senses.
        Keys include 'Sight', 'Smell', 'Taste','Touch',
        and 'Sound', while values are either booleans.
        '''
        return {
            'Sight': False,
            'Smell': False,
            'Taste': False,
            'Touch': False,
            'Sound': False
        }


    @property
    def image_url(self) -> List[str]:
        '''
        The list of URLs to images uploaded by the user. 
        '''
        return []


    @property
    def report_type(self) -> List:
        '''
        A list of complaint report types.
        '''
        return ['Wells']

