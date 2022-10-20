import os

# Directories
ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIRECTORY = f"{ROOT_DIRECTORY}/tests/screenshots"
MOCK_LOCATIONS_FILE = f"{ROOT_DIRECTORY}/tests/data/mock_locations.json"

# Development environment
PROD_ENV = os.getenv('PROD_ENV')
DEV = 'dev'
TEST = 'test'
PROD = 'prod'