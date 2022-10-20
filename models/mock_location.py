'''
mock_location.py
'''

from models.base_location import Location


class MockLocation(Location):
    
    def __init__(
        self,
        lat: float,
        lon: float,
        state: str,
        zip: str,
        county: str,
        full_address: str) -> None:
        '''
        The constructor for the `MockLocation` class.

        Parameters:
            lat (float): The location latitude.

            lon (float): The location longitude.

            state (str): The location's state name (e.g., "Ohio").

            zip (str): The location's zip code.

            county (str): The location's state county (e.g., "Cuyahoga").

            full_address (str): The location's complete street address
                (e.g., as used for mailing).

        Returns:
            None
        '''
        self._lat = lat
        self._lon = lon
        self._state = state
        self._zip = zip
        self._county = county
        self._full_address = full_address


    @property
    def latitude(self) -> float:
        '''
        The location latitude. 
        '''
        return self._lat


    @property
    def longitude(self) -> float:
        '''
        The location longitude. 
        '''
        return self._lon


    @property
    def state(self) -> str:
        '''
        The location state. 
        '''
        return self._state


    @property
    def zip(self) -> str:
        '''
        The test location's zip code. 
        '''
        return self._zip

    
    @property
    def county(self) -> str:
        '''
        The test location's state county.
        '''
        return self._county


    @property
    def full_address(self) -> str:
        '''
        The location's complete street address. 
        '''
        return self._full_address


    @property
    def is_valid(self) -> bool:
        '''
        A boolean indicating whether the location has been marked as valid. 
        '''
        return True

