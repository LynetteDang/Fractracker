'''
state_email.py

Emails the state agencies with environmental complaints.
'''

import os
from datetime import datetime
from models.base_report import Report
from utilities.sendgrid_email import SendGridEmail

class StateEmail:
    '''
    Represents an environmental complaint sent to a state agency.
    '''

    def __init__(
        self,
        report: Report,
        to_email: str,
        from_email: str,
        cc_email: str,
        agency: str,
        subject: str) -> None:
        '''
        The public constructor.

        Parameters:
            report (Report): The complaint from the FracTracker API.

            to_email (str): The agency's email address. A test value
                should be used in non-production environments.

            from_email (str): The person or organization sending the email.

            cc_email (str): The email address of the FracTracker mobile
                app user. A test value should be used in non-production
                environments.

            agency (str): The name of the state agency receiving the email.

            subject (str): The email subject line to use.

        Returns:
            None
        '''
        self.report=report,
        self.to_email= to_email,
        self.from_email=from_email,
        self.cc_email=cc_email,
        self.agency= agency,
        self.subject= subject


    def _append_num_suffix(self, num: int):
        '''
        Appends the appropriate English suffix to a number.
        Example: '3' would become '3rd' and '212', '212th'.

        Parameters:
            num (int): The number.

        Returns:
            (str): The formatted number.
        '''
        num_str = str(num)
        last_two_digits = num_str[-2:] if len(num_str) > 1 else num_str
        four_thru_nineteen = [str(i) for i in range(4, 20)]

        if last_two_digits in four_thru_nineteen:
            return f'{num_str}th'
        if num_str.endswith('1'):
            return f'{num_str}st'
        if num_str.endswith('2'):
            return f'{num_str}nd'
        if num_str.endswith('3'):
            return f'{num_str}rd'
        else:
            return f'{num_str}th'


    def _create_email_message(self) -> str:
        '''
        Creates an email message body from a FracTracker report.

        Parameters:
            report (Report): A single complaint from the FracTracker API.

        Returns:
            (str): The email body.
        '''
        # Standardize date
        date = datetime.fromisoformat(self.report.date)
        month = date.strftime("%B")
        formatted_date = f"{month} {self._append_num_suffix(date.day)}"

        # Handle situations with missing first or last name
        missing_name = not self.report.first_name or not self.report.last_name
        full_name = '' if missing_name else f'{self.report.first_name} {self.report.last_name}'
        intro = '' if missing_name else f'Hi, my name is {full_name}. '
        closing = '' if missing_name else f'\n\nSincerely,\n{full_name}'

        # Handle missing county
        county = '' if not self.report.location.county else f' in {self.report.location.county}'

        # Handle missing images
        img_ackgmt = '' if not self.report.image_url else 'find supporting images attached and '

        # Handle missing description and add details from report
        description = '.' if not self.report.description else '. In the app, I included the ' + \
            f'following description: "{self.report.description}".'

        # Compose message
        message = f'To the {self.agency}:\n\n{intro}On {formatted_date}, I reported an environmental ' + \
            'complaint using the FracTracker mobile app and agreed that it be forwarded ' + \
            f'to your agency. The incident I witnessed occurred at roughly ' + \
            f'{self.report.lat:.4f} degrees latitude and {self.report.lon:.4f} degrees longitude' + \
            f'{county}{description} Please {img_ackgmt}contact me directly at {self.report.email}' + \
            f' to follow up with next steps. Thank you, and have a great day!{closing}'

        return message


    def email_agency(self) -> None:
        '''
        Emails a governmental agency to report an environmental
        complaint submitted by a FracTracker mobile app user.

        Parameters:
            None

        Returns:
            None
        '''
        # Retrieve API key from environmental variables
        try:
            sendgrid_api_key = os.environ['SENDGRID_API_KEY']
        except KeyError:
            raise Exception(f"Failed to send email to {self.to_email}. "
                "Missing SendGrid API key.")

        if type(self.report) == tuple:
            self.report = self.report[0]
        if type(self.from_email) == tuple:
            self.from_email = self.from_email[0]
        if type(self.to_email) == tuple:
            self.to_email = self.to_email[0]
        if type(self.subject) == tuple:
            self.subject = self.subject[0]
        if type(self.cc_email) == tuple:
            self.cc_email = self.cc_email[0]
        if type(self.agency) == tuple:
            self.agency = self.agency[0]
        # Initialize email
        message_body = self._create_email_message()

        sendgrid_email = SendGridEmail(
            sendgrid_api_key,
            message_body,
            self.from_email,
            self.to_email,
            self.subject,
            self.cc_email
        )
        for idx, url in enumerate(self.report.image_url):
            sendgrid_email.add_attachment_online(f"image{idx+1}.jpg", url)

        # Send email
        sendgrid_email.send()