'''
base_location.py
'''

import json
from abc import ABC, abstractproperty


class Location(ABC):
    '''
    An abstract version of a FracTracker complaint location.
    Enforces the existence of expected properties for subclasses.
    '''

    @abstractproperty
    def latitude(self) -> float:
        '''
        The location latitude. 
        '''
        raise NotImplementedError


    @abstractproperty
    def longitude(self) -> float:
        '''
        The location longitude. 
        '''
        raise NotImplementedError


    @abstractproperty
    def state(self) -> str:
        '''
        The location state. 
        '''
        raise NotImplementedError


    @abstractproperty
    def zip(self) -> str:
        '''
        The location zip code. 
        '''
        raise NotImplementedError

    
    @abstractproperty
    def county(self) -> str:
        '''
        The location state county. 
        '''
        raise NotImplementedError

    
    @property
    def full_address(self) -> str:
        '''
        The location's complete street address. 
        '''
        raise NotImplementedError


    @abstractproperty
    def is_valid(self) -> bool:
        '''
        A boolean indicating whether the location has been marked as valid. 
        '''
        raise NotImplementedError


    def __str__(self) -> str:
        '''
        Overrides the default implementation for representing
        a `Location` instance as an informal string.
        '''
        return (f'Location(lat={self.latitude}, lon={self.longitude}, '
            f'is_valid={self.is_valid}, state={self.state}, '
            f'full_address={self.full_address}, zip={self.zip}, '
            f'county={self.county})')


    def __repr__(self) -> str:
        '''
        Overrides the default implementation for representing
        a `Location` instance as an official string.
        '''
        return json.dumps(vars(self), indent=2)

