'''
test_fractracker_api.py

Unit tests run against the FracTracker API utility class.
'''

import unittest
import datetime
from utilities.fractracker_api import FracAPI


class TestFracAPI(unittest.TestCase):

    def test_date_format(self):
        '''
        Test that a value error is raised for an incorrect date format.
        '''
        with self.assertRaises(ValueError):
            FracAPI("30-12-2020")


    def test_query_by_date(self):
        '''
        Test that future date returns assertion error. 
        '''
        future_date = datetime.date.today() + datetime.timedelta(days=2)
        with self.assertRaises(AssertionError):
            FracAPI(future_date.strftime("%m-%d-%Y"))


    def test_json_format(self):
        '''
        Test json format by checking latitude and longitude.
        '''
        api_results = FracAPI("07-04-2021")

        sample_report = api_results.reports[0]
        # TODO Update test with new Report framework
        # [lon, lat] format
        #self.assertLess(sample_report.lon, 0, 'Longitude is incorrect')
        #self.assertGreater(sample_report.lat, 0, 'Latitude is incorrect')
        pass


    def test_num_correct_reports(self):
        '''
        Test that the correct number of reports are return for a date range.
        '''
        TEST_BEGIN = "07-04-2021"
        TEST_END = "10-11-2021"
        CORRECT_NO_RESULTS = 7
        api_results = FracAPI(begin_date=TEST_BEGIN, end_date=TEST_END)
        self.assertEqual(len(api_results.reports), CORRECT_NO_RESULTS, 
                         'Number of reports returned is incorrect')


if __name__ == '__main__':
    unittest.main()
