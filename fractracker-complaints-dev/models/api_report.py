'''
api_report.py

Takes in a single json report and creates attributes from json items.
'''

from models.base_location import Location
from models.base_report import Report
from typing import Dict, List
from models.geocoded_location import GeocodedLocation
from validate_email import validate_email


class ApiReport(Report):
    '''
    Class to store relevant report information from FracTracker API JSON.
    '''
    
    def __init__(self, json:dict, check_emails:bool=True) -> None:
        '''
        The constructor for the `Report` class.

        Parameters: 
            json (dict): A single report from the FracTracker API.

            check_emails (bool): Indicates whether to check the
                validity of the report's associated email address.
                Defaults to True.

        Returns:
            None
        '''
        # Extract report metadata
        self._id = json['id']
        
        # Extract first level data
        props_level_1 = json['properties']
        self._description = props_level_1['description']
        self._date = props_level_1['report_date']

        # Extract second level data
        props_level_2 = props_level_1['created_by']['properties']
        self._first_name = props_level_2['first_name'] if not props_level_2['first_name'] else 'NA'
        self._last_name = props_level_2['last_name'] if not props_level_2['last_name'] else 'NA'
        self._email = props_level_2['email']

        # Validate email address if indicated
        if check_emails:
            self.email_is_valid = validate_email(email_address=self._email)

        # Extract more complicated data from json
        self._lat, self._lon = None, None
        self._location = self.get_location(json)
        self._senses = self.get_senses(json)
        self._image_url = self.get_val_from_list(json, 'images', 'original')
        self._report_type = self.get_val_from_list(json, 'industries', 'name')


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
        return self._description


    @property
    def date(self) -> str:
        '''
        The date on which the report was submitted.
        '''
        return self._date

    
    @property
    def first_name(self) -> str:
        '''
        The first name of the FracTracker user submitting the report. 
        '''
        return self._first_name


    @property
    def last_name(self) -> str:
        '''
        The last name of the FracTracker user submitting the report. 
        '''
        return self._last_name


    @property
    def email(self) -> str:
        '''
        The email address of the FracTracker user submitting the report. 
        '''
        return self._email


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
        return self._senses


    @property
    def image_url(self) -> List[str]:
        '''
        The list of URLs to images uploaded by the user. 
        '''
        return self._image_url


    @property
    def report_type(self) -> List:
        '''
        A list of complaint report types.
        '''
        return self._report_type
    
    
    def get_location(self, json):
        '''
        Method to add attribute location (an instance of Location class).

        Inputs: json: json-formatted dictionary of report from API
        Returns: instance of Location class
        '''
        # Some coords found in "geometries", others found directly in "coords"
        geometry = json['geometry']
        if 'geometries' in geometry.keys():
            coords = geometry['geometries'][0]['coordinates']    
        else:
            coords = geometry['coordinates']
        self._lat, self._lon = coords[1], coords[0]
        return GeocodedLocation(lat=self._lat, lon=self._lon)


    def get_senses(self, json):
        '''
        Method to check if each sense was listed in report.

        Inputs: json: json-formatted dictionary of report from API.
        Returns: a dictionary of keys = senses, and values = bools.
        '''
        senses = ['Sight', 'Smell', 'Taste','Touch','Sound']
        senses_dict = {sense: False for sense in senses}

        for s in json['properties']['senses']:
            sense = s['properties']['name']
            senses_dict[sense] = True
        return senses_dict


    def get_val_from_list(self, json, prop_type, item_type):
        '''
        Method to extract value from a list within the json. List may be empty.
        Inputs:
         - json: json-formatted dictionary of report from API.
         - prop_type: (string) type of property ("images" or "industries")
         - item_type: (string) name of item ("original" or "name")
        returns: attr (string) of attribute (image url or industry name)
        '''
        item_list = json['properties'][prop_type]
        return [s['properties'][item_type] for s in item_list]

