import imaplib
import re
from pprint import pprint

from imap_tools import A, MailBox


class ImapHandler:
    def __init__(self, user, password):
        # self.host = 'imap.gmail.com'
        self.host = 'imap.gmx.com'
        self.imap_ssl_port = 993
        self.user = user
        self.password = password
        self.text_pattern = """
                We received a request to create a new AWS account using this e-mail address.
                We could not complete your request because an AWS account is already associated with this e-mail address.
                If the account associated with this e-mail address is active, you can sign in using the following link:
                https://console.aws.amazon.com/console/home
                """

    def get_confirm_message(self):
        imap = imaplib.IMAP4_SSL(self.host)
        imap.login(self.user, self.password)
        imap.select('Inbox')

        tmp, messages = imap.search(None, 'INBOX')
        for num in messages[0].split():
            tmp, data = imap.fetch(num, '(RFC822)')
            pprint(data)
        imap.close()
        imap.logout()

    def mailbox_confirm_message(self):

        verify_codes = ['']
        with MailBox(self.host).login(self.user, self.password, 'INBOX') as mailbox:
            for msg in mailbox.fetch(A(new=True)):
                sender = msg.from_
                if sender in ['amazonaws', 'no-reply@amazonaws.com', 'no-reply@signup.aws']:
                    body = msg.text
                    match = re.search(r"\b\d{6}\b", body)
                    if match:
                        code = match.group()
                        print(f"Verification code: {code}")
                        verify_codes.append(code)
                # if 'create a new AWS' in msg.text:
                #     print(msg.date)
                #     return self.extract_link_from_text(msg.text)
        print(f'all verify codes: {verify_codes}')
        return verify_codes[-1]

    def extract_link_from_text(self, text):
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, text)
        if urls[0]:
            print(f"Extracted link: {urls[0]}")
        else:
            print("No link found in the text.")
        return urls[0] if urls else None
