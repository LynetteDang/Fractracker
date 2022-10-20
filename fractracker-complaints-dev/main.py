'''
main.py

Triggers the submission of complaints submitted by FracTracker
users to state agencies by querying FracTracker's internal API
for new reports, routing the reports to the appropriate states,
and submitting the data through a web form or email. 
'''

import datetime
import json
import os
import pandas as pd
from constants import MOCK_LOCATIONS_FILE, PROD, PROD_ENV, TEST
from flask import Flask, request
from models.base_report import Report
from models.mock_report import MockReport
from models.submission import Submission
from utilities.config import Config
from utilities.fractracker_api import FracAPI
from utilities.logger import logger
from utilities.storage import LocalDatastore, CloudDatastore
from typing import List

# Initialize global variables
app = Flask(__name__)
config = Config()

# Set datastore
if PROD_ENV in (TEST, PROD):
    datastore = CloudDatastore(config.cloud_bucket_name, config.cloud_blob_name)
else:
    datastore = LocalDatastore(config.metadata_path)

@app.route("/", methods = ['POST'])
def submit_complaints():
    '''
    Main execution logic for program. Orchestrates submission of
    complaint data from the FracTracker API to corresponding
    state and sub-state agencies through emails and web
    form submissions.
    '''
    try:
        logger.info(f'Beginning program execution. Current environment is {PROD_ENV}.')

        logger.info("Parsing request body for inclusive start and end date of report retieval.")
        request_body = request.get_json()
        start_date = request_body.get('start_date')
        end_date = request_body.get('end_date')

        logger.info("Retrieving reports.")
        reports = get_mock_reports() if PROD_ENV == TEST else get_api_reports(start_date, end_date)
        num_reports = len(reports)

        if not num_reports:
            msg = "No reports found in timespan."
            logger.info(msg)
            return msg, 200

        logger.info(f"{len(reports)} report(s) found. Starting submission process.")
        metadata_df = submit_reports(reports)

        logger.info(f'Submitted all state emails/web forms. Updating metadata.')
        datastore.write_data(metadata_df)

        logger.info("Automated complaint submission complete.")
        return "Automated complaint submission complete.", 201

    except Exception as e:
        msg = f"Automated complaint submission failed. {e}"
        logger.error(msg)
        return msg, 500


def get_mock_reports() -> List[Report]:
    '''
    Generates mock FracTracker reports from a JSON file.

    Parameters:
        None

    Returns:
        (list of Report): The mock reports.
    '''
    try:
        logger.info('Reading mock location data from file.')
        with open(MOCK_LOCATIONS_FILE) as f:
            mock_locations = json.load(f)
        return [MockReport(loc) for loc in mock_locations]
    except Exception as e:
        raise Exception(f"Failed to generate mock reports. {e}")


def get_api_reports(
    begin_date: str=None,
    end_date: str=None) -> List[Report]:
    '''
    Retrieves FracTracker complaint reports from the API.
    The default is to retrieve reports from the last 24 hours.

    Parameters:
        begin_date (str): The inclusive start date for which
            to query for FracTracker API reports.

        end_date (str): The inclusive end date for which to
            query for FracTracker API reports.

    Returns:
        (list of Report): The reports.
    '''
    if not begin_date or not end_date:
        now = datetime.datetime.now()
        end_date = now.strftime("%m-%d-%Y")
        begin_date = (now - datetime.timedelta(days=1)).strftime("%m-%d-%Y")
        
    logger.info("Querying FracTracker API for reports dated "
        f"between {begin_date} and {end_date}, inclusive.")

    try:
        api_results = FracAPI(
            begin_date=begin_date,
            end_date=end_date, 
            check_emails=False)
    except Exception as e:
        raise Exception(f"Failed to retrieve reports from API. {e}")

    return api_results.reports
   

def submit_reports(reports: List[Report]) -> pd.DataFrame:
    '''
    Submits a given list of reports to their respective state
    agencies and aggregates submission metadata.

    Parameters:
        reports (list of Report): The reports to submit.

    Returns:
        (pd.DataFrame): The returned metadata.
    '''
    # Get previous submissions
    metadata_df = datastore.read_data()
    
    for report in reports:
        if len(metadata_df.index)==0 or (
            report.id not in metadata_df["id"].values):
            metadata_list = Submission(report).metadata
            for meta in metadata_list:
                metadata_df = metadata_df.append(vars(meta), ignore_index=True)

    return metadata_df


if __name__ == "__main__":
    debug = PROD_ENV != PROD
    host = os.environ.get("HOST", config.default_app_host)
    port = int(os.environ.get("PORT", config.default_app_port))
    app.run(debug=debug, host=host, port=port)
