'''
api_duplicates.py

Module to look at duplicates within data from FracTracker API.
'''

import pandas as pd
import os
import sys

# Ensure main path is added so we can import new modules
main_dir = os.getcwd()
if "utilities" in main_dir:
    main_dir = os.path.dirname(main_dir)
sys.path.append(main_dir)

from utilities.api_report import Report
from utilities.fractracker_api import FracAPI

# Get all results from FracTracker API (first reports ~2014)
api_results = FracAPI("01-01-2010")
print("Queried API")

df = pd.DataFrame()

for r in api_results.reports:
    d = {"id":[r.id],
        "lon":[r.lon],
        "lat":[r.lat],
        "first_name":[r.first_name],
        "last_name":[r.last_name],
        "email":[r.email],
        "description":[r.description],
        "date":[r.date],
        "image_url":[r.image_url],
        "senses":[r.senses],
        "report_type":[r.report_type]}
    new_df = pd.DataFrame(d)
    df = df.append(new_df)

# Save as csv to look at more easily
df.to_csv("api_data/all_api_reports.csv")

# Save another with just the duplicates
dup_cols = [c for c in df.columns if c not in ['id', 'image_url', 'senses']]
df[df.duplicated(subset=dup_cols,keep=False)].to_csv('api_data/duplicates.csv')
print('DONE')
