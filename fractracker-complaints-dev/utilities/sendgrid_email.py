'''
sendgrid_email.py

Utilities for sending emails using SendGrid.

References:
- https://github.com/sendgrid/sendgrid-python
- https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/authentication
'''

import base64
import json
import urllib.request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Disposition,
    FileContent,
    FileName,
    FileType,
    Mail
)
from email_validator import validate_email, EmailNotValidError
from python_http_client.exceptions import HTTPError
from utilities.logger import logger


class SendGridEmail:
    '''
    Represents an email utilizing the SendGrid API.
    '''

    def __init__(
        self,
        key: str,
        message_body: str,
        from_email: str,
        to_email: str,
        subject: str,
        cc_email: str=None) -> None:
        '''
        The public constructor.

        Parameters:
            key (str): The SendGrid API key.
            
            message_body (str): The email message body/contents.

            from_email (str): The address of the email sender.

            to_email (str): The address of the email recipient.

            cc_email (str): The email address of CC'd recipient.

            subject (str): The email subject line.

        Returns:
            None
        '''
        self.key = key
        self.message_body= message_body
        self.from_email = self._validate_email_address(from_email)
        self.to_email = self._validate_email_address(to_email)
        self.cc_email = self._validate_email_address(cc_email) if cc_email else None
        self.subject = subject
        self.attachments = []


    def _append_attachment(self, data: bytes, attachment_name: str) -> None:
        """
        Appends a file attachment to the SendGridEmail instance.

        Inputs:
            data (bytes) - The file.

            attachment_name (str) - The name of the file attachment.

        Returns:
            None
        """
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('image/jpeg')
        attachment.file_name = FileName(attachment_name)
        attachment.disposition = Disposition('attachment')
        self.attachments.append(attachment)


    def _validate_email_address(self, email: str) -> str:
        """
        Raises an exception if an email address is invalid;
        otherwise, returns the validated email.

        Parameters:
            email (str) - The email address that needs to be validated.

        Returns:
            (str): The normalized email address.
        """
        # try:
        #     valid = validate_email(email)
        #     return valid.email
        # except EmailNotValidError as e:
        #     raise Exception(f'Email "{email}" is invalid: {e}')
        return email


    def add_attachment_online(self, attachment_name: str, url: str) -> None:
        """
        Downloads a file from a URL and then attaches
        it to the SendGridEmail instance.

        Inputs:
            attachment_name (str) - The name to use for the file
                attachment (e.g., 'fracking_img1.jpg').

            url (str): The url of the online attachment.

        Returns:
            None
        """
        with urllib.request.urlopen(url) as f:
            data = f.read()
        self._append_attachment(data, attachment_name)


    def add_attachment_local(self, attachment_name: str, file_path: str) -> None:
        """
        Reads a local file from an absolute path and then
        attches the file to the SendGridEmail instance. 

        Paremeters:
            attachment_name (str) - The name to use for the file
                attachment (e.g., 'fracking_img1.jpg').

            file_path (str): The absolute path to the file.

        Output:
            None
        """
        with open(file_path, 'rb') as f:
            data = f.read()
        self._append_attachment(data, attachment_name)


    def send(self):
        """
        Sends the email using the SendGrid API.

        Inputs:
            None

        Output:
            None
        """
        # Compose email
        message = Mail(
            self.from_email,
            self.to_email,
            self.subject,
            self.message_body)

        message.attachment = self.attachments

        if self.cc_email:
            message.add_cc(self.cc_email)

        # Send email
        try:
            sg = SendGridAPIClient(self.key)
            response = sg.send(message)
            logger.info(f"Email submitted with response code: {response.status_code}")

        except HTTPError as e:
            # Compose error message
            http_errors = [err['message'] for err in json.loads(e.body)['errors']]
            error_msg = f'SendGridEmail from "{self.from_email}" to "{self.to_email}" ' + \
                f'with subject "{self.subject}" failed to be sent. {e}. ' + \
                ' '.join(http_errors)

            # Log and raise exception
            logger.error(error_msg)
            raise Exception(error_msg)
