'''
logger.py

Configures a logger for standard input.
'''

import logging

# Create logger
logger = logging.getLogger("fractracker")
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)


if __name__ == "__main__":
    logger.debug('This will get logged')
