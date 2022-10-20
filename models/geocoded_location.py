'''
geocoded_location.py
'''

import geopy
import numpy as np
from geopy.extra.rate_limiter import RateLimiter
from models.base_location import Location

    
class GeocodedLocation(Location):
    '''
    Utilizes the open source reverse geocoding library
    Nominatim to capture information associated with a
    given latitude and longitude, such as street address,
    city, state, and/or county data.
    '''

    def __init__(self, lat: float, lon: float) -> None:
        '''
        The constructor for `Location`.

        Parameters:
            lat (float): The location's latitude.

            lon (float): The location's longitude.

        Returns:
            None
        '''
        # Initialize properties
        self._lat = lat
        self._lon = lon
        self._is_valid = False
        self._state = self._zip = self._county = self._full_address = None

        # Return empty location if coordinates invalid 
        if not self._is_valid_latlon(lat, lon):
            return

        # Attempt to reverse geocode coordinates
        geolocator = geopy.Nominatim(user_agent='def', timeout=30)
        geocode = RateLimiter(
            func=geolocator.reverse,
            min_delay_seconds=1,
            return_value_on_exception=None
        ) 
        location = geocode((lat, lon))

        # Return empty location if geocoding failed:
        if not location:
            return

        # Parse location for remaining properties
        self._is_valid = True
        self._state = location.raw['address']["state"]
        try:
            self._full_address = location.raw['display_name']
        except:
            self._full_address = None
        try:
            self._zip = location.raw['address']["postcode"]
        except:
            self._zip = None
        try:
            self._county = location.raw['address']["county"]
        except:
            self._county = None


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
        The location zip code. 
        '''
        return self._zip

    
    @property
    def county(self) -> str:
        '''
        The location state county. 
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
        return self._is_valid


    def _is_valid_latlon(self, lat:float, lon:float) -> bool:
        """
        Validates a coordinate pair. See:
        http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost

        Inputs:
            lat (float): The latitude value.
            lon (float): The longitude value.
        
        Output:
            (boolean)
        """
        return (
            np.isfinite(lat) and 
            lat > 0 and
            lat <= 90 and
            np.isfinite(lon) and 
            lon < 0 and
            lon >= -180
        )

