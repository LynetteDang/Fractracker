'''
test_send_grid_email.py

Tests for functionality of email_test.py
'''
# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sys
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, FileContent, FileName, FileType,\
    ContentId, attachment
from configparser import ConfigParser
from sendgrid.helpers.mail import subject
from sendgrid.helpers.mail.subject import Subject

# Ensure main path is added so we can import new modules
sys.path.append(os.getcwd())
from utilities.send_grid_email import SendGridEmail

import unittest
from utilities.logger import logger

# initialize variables that are passed in as parameters for unit testing
FILE_PATH = ['test.pdf', 'test_2.pdf', 'test_3.pdf']
ATTACHMENT_NAME = ['test.pdf', 'test_2.pdf', 'test_3.pdf']
URL = ['https://polisci.ucsd.edu/undergrad/departmental-honors-and-\pi-sigma-alpha/L.-Dang_Senior-Honors-Thesis.pdf',
       'https://polisci.ucsd.edu/undergrad/departmental-honors-and-pi-sigma-alpha/A.-Garcia_Senior-Honors-Thesis.pdf']
# set up the path to base directory for local attachment purposes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESSAGE_BODY_LOCAL = 'email with multiple local file attachments'
MESSAGE_BODY_ONLINE = 'email with multiple online file attachments'
config = ConfigParser()
config.read('sendgrid.env')
KEY = config['sendgrid']['SENDGRID_API_KEY']
FROM_EMAIL = config['teststate']['from_email']
TO_EMAIL = config['teststate']['to_email']
CC_EMAIL = config['teststate']['cc_email']
SUBJECT = config['teststate']['subject']

class TestEmailModule(unittest.TestCase):

    def test_local_attachments(self):
        '''
        Unit Test with multiple local file attachments
        '''
        send_grid_email = SendGridEmail(KEY, MESSAGE_BODY_LOCAL, FROM_EMAIL, \
            TO_EMAIL, CC_EMAIL, SUBJECT)
        for i,x in enumerate(FILE_PATH):
            send_grid_email.add_attachment_local(os.path.join(BASE_DIR, x), \
                ATTACHMENT_NAME[i])
        send_grid_email.send()
        # current logger statement does not work, will address later
        # logger.log("Email with multiple local file attachmentssent successful")

        pass

    def test_online_attachments(self):
        '''
        unit test with multiple online file attachments
        '''
        send_grid_email = SendGridEmail(KEY, MESSAGE_BODY_ONLINE, FROM_EMAIL, \
            TO_EMAIL, CC_EMAIL, SUBJECT)
        for i,x in enumerate(URL):
            send_grid_email.add_attachment_online(ATTACHMENT_NAME[i], x)
        send_grid_email.send()
        # current logger statement does not work, will address later
        # logger.log("Email with multiple local file attachmentssent successful")

        pass

if __name__ == '__main__':
    unittest.main()