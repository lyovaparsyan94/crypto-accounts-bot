import re

from imap_tools import A, MailBox
from logs.aws_logger import awslogger


class ImapHandler:
    def __init__(self, user: str, password: str) -> None:
        """
        Initialize an ImapHandler instance.

        Args:
            user (str): The IMAP user (email address).
            password (str): The IMAP password.
        """
        # self.host = 'imap.gmail.com'
        self.host = 'imap.gmx.com'
        self.imap_ssl_port = 993
        self.user = user
        self.password = password

    def mailbox_confirm_message(self) -> str:
        """
        Extract the latest verification code from AWS service.

        Returns:
            str: The latest verification code found in the inbox.
        """
        verify_codes = ['']
        with MailBox(self.host).login(self.user, self.password, 'INBOX') as mailbox:
            for msg in mailbox.fetch(A(all=True)):
                sender = msg.from_
                if sender in ['amazonaws', 'no-reply@amazonaws.com', 'no-reply@signup.aws']:
                    body = msg.text
                    match = re.search(r"\b\d{6}\b", body)
                    if match:
                        code = match.group()
                        awslogger.log_info(f"Verification code: {code}")
                        verify_codes.append(code)
        awslogger.log_info(f'all verify codes: {verify_codes}')
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
        if urls[0]:
            awslogger.log_info(f"Extracted link: {urls[0]}")
        else:
            awslogger.log_info("No link found in the text.")
        return urls[0] if urls else None
