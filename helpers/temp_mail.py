import re
import time
from time import sleep
from tempmail import EMail


def generate_mail():
    email = EMail()
    email = email.address
    print(f"generated: {email}")
    return email


def check_last_message(email, retry=5, interval=5):
    time.sleep(5)
    email = EMail(email)
    inbox = email.get_inbox()
    if len(inbox) == 0:
        print('inbox is empty')
        return False
    messages = []
    while not messages and retry >= 1 and len(inbox) > 0:
        try:
            for msg in inbox:
                sender = msg.from_addr
                if sender in ['.aws', 'no-reply@amazonaws.com', 'no-reply@signup.aws'] or 'aws' in sender:
                    body = msg.message.text_body
                    match = re.search(r"\b\d{6}\b", body)
                    if match:
                        code = match.group()
                        print(f"Verification code: {code}")
                        messages.append(code)
        except BaseException as e:
            retry -= 1
            sleep(interval)
            print(f"Verify code not found, retrying {5 - retry}")
    return messages[-1]

