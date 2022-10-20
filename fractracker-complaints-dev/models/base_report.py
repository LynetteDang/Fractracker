'''
base_report.py
'''

from abc import ABC, abstractproperty
from models.base_location import Location
from typing import Dict, List


class Report(ABC):
    '''
    An abstract version of a FracTracker complaint report.
    Enforces the existence of expected properties for subclasses.
    '''

    @abstractproperty
    def id(self) -> str:
        '''
        The report id.
        '''
        raise NotImplementedError


    @abstractproperty
    def lat(self) -> float:
        '''
        The latitude of the incident described by the report. 
        '''
        raise NotImplementedError


    @abstractproperty
    def lon(self) -> float:
        '''
        The longitude of the incident described by the report. 
        '''
        raise NotImplementedError


    @abstractproperty
    def description(self) -> str:
        '''
        The report description. 
        '''
        raise NotImplementedError


    @abstractproperty
    def date(self) -> str:
        '''
        The date on which the report was submitted.
        '''
        raise NotImplementedError

    
    @abstractproperty
    def first_name(self) -> str:
        '''
        The first name of the FracTracker user submitting the report. 
        '''
        raise NotImplementedError


    @abstractproperty
    def last_name(self) -> str:
        '''
        The last name of the FracTracker user submitting the report. 
        '''
        raise NotImplementedError


    @abstractproperty
    def email(self) -> str:
        '''
        The email address of the FracTracker user submitting the report. 
        '''
        raise NotImplementedError


    @abstractproperty
    def location(self) -> Location:
        '''
        The location in which the user observed an incident. 
        '''
        raise NotImplementedError


    @abstractproperty
    def senses(self) -> Dict:
        '''
        A dictionary enumerating affected user senses.
        Keys include 'Sight', 'Smell', 'Taste','Touch',
        and 'Sound', while values are either booleans.
        '''
        raise NotImplementedError


    @abstractproperty
    def image_url(self) -> List[str]:
        '''
        The list of URLs to images uploaded by the user. 
        '''
        raise NotImplementedError


    @abstractproperty
    def report_type(self) -> List:
        '''
        A list of complaint report types.
        '''
        raise NotImplementedError


    def __str__(self) -> str:
        '''
        Overrides the default implementation for representing
        a `Report` instance as a string.

        Parameters:
            None

        Returns:
            (str): The string reprsentation.
        '''
        return (f'Report(id={self.id}, lat={self.lat}, lon={self.lon}, '
            f'description={self.description}, date={self.date}, '
            f'first_name={self.first_name}, last_name={self.last_name}, '
            f'email={self.email}, location={self.location}, senses={self.senses}, '
            f'image_url={self.image_url}, report_type={self.report_type})')

    
    def __repr__(self) -> str:
        '''
        Overrides the default implementation for representing
        a `Report` instance as a string.

        Parameters:
            None

        Returns:
            (str): The string reprsentation.
        '''
        return str(vars(self))


    def __eq__(self, other) -> bool:
        '''
        Method to compare one instance of BaseReport to another.

        Parameters:
            other (Report): A report to compare against.

        Returns:
            (bool): True if both reports contain the same attributes, 
                excluding images and id (which are always unique) and
                False otherwise.
        '''
        if isinstance(other, Report):
            return self.date == other.date and \
                   self.description == other.description and \
                   self.first_name == other.first_name and \
                   self.last_name == other.last_name and \
                   self.lon == other.lon and self.lat == other.lat
        return False
