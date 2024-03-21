import re
import imaplib
from pprint import pprint
from imap_tools import MailBox, A


class ImapHandler:
    def __init__(self, user, password):
        self.host = 'imap.gmail.com'
        self.imap_ssl_port = 993
        self.user = user
        self.password = password

    # def get_confirm_message(self):
    #     imap = imaplib.IMAP4_SSL(self.host)
    #     imap.login(self.user, self.password)
    #     imap.select('Inbox')
    #
    #     # tmp, messages = imap.search(None, 'ALL')
    #     # for num in messages[0].split():
    #     #     tmp, data = imap.fetch(num, '(RFC822)')
    #     #     print('tmp', tmp)
    #     #     pprint(data)
    #     #     break
    #     imap.close()
    #     imap.logout()

    def mailbox_confirm_message(self):
        verify_codes = [None]
        with MailBox(self.host).login(self.user, self.password, 'INBOX') as mailbox:
            for msg in mailbox.fetch(A(all=True)):
                sender = msg.from_
                if sender in ['amazonaws', 'no-reply@amazonaws.com', 'no-reply@signup.aws']:
                    body = msg.text
                    match = re.search(r"\b\d{6}\b", body)
                    if match:
                        code = match.group()
                        print(f"Verification code: {code}")
                        verify_codes.append(code)
                        # return code
                    else:
                        print("not found code.")
        print(verify_codes[-1])
        return verify_codes[-1]


# a = ImapHandler("dorothylft78qc@gmail.com", 'aizv rivk yvjo snkc')
# b = a.mailbox_confirm_message()
