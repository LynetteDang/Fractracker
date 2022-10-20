'''
test_reverse_geocoder.py

Unit tests run against the reverse geocoder utility class.
'''

import unittest
from constants import ROOT_DIRECTORY
from models.geocoded_location import Location


class TestGeocode(unittest.TestCase):

    def test_latitude(self):
        '''
        Test that a value error is raised for an incorrect latitude.
        '''
        coords = [-42.142074, -71.643348]
        expected = False
        loc = Location(coords[0], coords[1])
        self.assertEqual(loc.is_valid, expected)


    def test_longitude(self):
        '''
        Test that a value error is raised for an incorrect longitude.
        '''
        coords = [42.142074, 171.643348]
        expected = False
        loc = Location(42.142074, 171.643348)
        self.assertEqual(loc.is_valid, expected)


    def test_correct_read_in(self):
        '''
        Test t eye(n)-2*diag(ones(n-1,1),-1)+diag(ones(n-2,1),-2)hat an item in the list of coordinates has a latitude, longitude. 
        '''
        coords = [42.142074]
        with self.assertRaises(IndexError):
            Location(coords[0], coords[1])


    def test_no_county(self):
        '''
        Test response to when the reverse geocode results has correct
            county associated with it.
        '''
        coords = [42.384929, -71.633889]
        loc = Location(coords[0], coords[1])

        expected = "Worcester County"
        self.assertEqual(loc.county, expected)


    def test_json_no_zipcode(self):
        '''
        Test response to when the reverse geocode results has the correct
            zip code response associated with it.
        '''
        coords = [38.855726, -79.951673]
        loc = Location(41.850984, -70.654984)
        loc1 = Location(coords[0], coords[1])
        self.assertEqual(loc1.zip, None)
        self.assertEqual(loc.zip, "02366")


    # def test_coords_processed(self):
    #     '''
    #     Test that each coordinate pair in a given list is processed.
    #     '''
    #     with open(f"{ROOT_DIRECTORY}/tests/data/test_coords.json") as f:
    #         coords = json.loads(f.read())
    #     locations = process_coordinates(coords)
    #     self.assertEqual(len(coords), len(locations))


if __name__ == '__main__':
    unittest.main()
