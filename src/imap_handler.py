import re

from imap_tools import A, MailBox
from logs.aws_logger import awslogger
from utils.element_handler import ElementHandler


class ImapHandler:
    def __init__(self, user: str, password: str, host: str = 'imap.gmx.com', imap_ssl_port: int = 993) -> None:
        """
        Initialize an ImapHandler instance.

        Args:
            user (str): The IMAP user (email address).
            password (str): The IMAP password.
        """
        # self.host = host
        self.host = 'imap.gmail.com'
        self.imap_ssl_port = imap_ssl_port
        self.user = user
        self.password = password
        self.sender = "no-reply@signup.aws"

    @ElementHandler.wait_for_result
    def mailbox_confirm_message(self) -> str:
        """
        Extract the latest verification code from AWS service.

        Returns:
            str: The latest verification code found in the inbox.
        """
        verify_codes = ['']
        with MailBox(self.host).login(self.user, self.password, '[Gmail]/All Mail') as mailbox:
            awslogger.log_info(f"checking email messages from: {self.sender}")
            for msg in mailbox.fetch(A(from_=self.sender)):
                awslogger.log_info('collecting ... ')
                body = msg.text
                match = re.search(r"\b\d{6}\b", body)
                if match:
                    code = match.group()
                    awslogger.log_info(f"Verification code: {code}")
                    verify_codes.append(code)
        awslogger.log_info(f'searching the last verify code in {verify_codes}')
        return verify_codes[-1]

    def extract_link_from_text(self, text: str) -> str | None:
        """
        Extract a URL link from the given text.

        Args:
            text (str): The text to search for URLs.

        Returns:
            str | None: The extracted URL link or None if no link is found.
        """
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, text)
        if len(urls) > 0:
            awslogger.log_info(f"Extracted link: {urls[0]}")
            return urls[0]
        else:
            awslogger.log_info("No link found in the text.")
            return None
