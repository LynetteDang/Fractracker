'''
check_locations.py

Check what location data is returned from the API query to confirm the results
of calling the geocoder on entire FracTracker Dataset
'''

from utilities.fractracker_api import FracAPI
import pandas as pd

# Set start date before all reports
START_DATE = "01-01-2000"
api_results = FracAPI(START_DATE)

df = pd.DataFrame()
report_vars = {}

# Remove some more complicated variables from object for simplicity
exclude_vars = ['location', 'email_is_valid', 'senses', 'image_url']

for r in api_results.reports:
    report_vars = {k:v for k,v in vars(r).items() if k not in exclude_vars}
    report_vars['location.is_valid'] = r.location.is_valid
    report_vars['location.zip'] = r.location.zip
    report_vars['location.county'] = r.location.county
    report_vars['location.state'] = r.location.state
    new_df = pd.DataFrame(report_vars)
    df = df.append(new_df)

# Save as csv to look at more easily
df.to_csv("data/all_api_report_locations.csv", index=False)
