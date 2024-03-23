import re
from time import sleep
from tempmail import EMail


def generate_mail():
    email = EMail()
    email = email.address
    print(email)
    return email


def check_last_message(email, retry=5, interval=5):
    email = EMail(email)
    inbox = email.get_inbox()
    messages = []
    if len(inbox) > 0:
        print('Inbox is not empty')
        while not messages and retry >= 1:
            try:
                for msg in inbox:
                    sender = msg.from_addr
                    if sender in ['.aws', 'no-reply@amazonaws.com', 'no-reply@signup.aws'] or 'signup.aws' in sender:
                        body = msg.message.text_body
                        match = re.search(r"\b\d{6}\b", body)
                        if match:
                            code = match.group()
                            print(f"Verification code: {code}")
                            messages.append(code)
            except BaseException as e:
                print(e)
                retry -= 1
                sleep(interval)
                print(f"Retrying {5 - retry} time after {interval} seconds interval")
        return messages[-1]


# check_last_message('qaoqelntgi@txcct.com')

