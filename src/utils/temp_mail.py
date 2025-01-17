import re
from time import sleep

from logs.aws_logger import awslogger
from tempmail import EMail


def generate_mail() -> str:
    """
    Generates a temporary email address for receive verification message from AWS then to it.

    Returns:
        str: The generated email address.
    """
    email = EMail()
    email = email.address
    awslogger.log_info(f"generated: {email}")

    return email


def check_last_message(email: str, retry: int = 5, interval: int = 5) -> bool | str:
    """
    Retrieves the last verification code from the email inbox.
    Returns:
        The last verification code if found, or False if the inbox is empty.
    """
    email = EMail(email)
    inbox = email.get_inbox()
    if len(inbox) == 0:
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
                        awslogger.log_info(f"Verification code: {code}")
                        messages.append(code)
        except BaseException:
            retry -= 1
            sleep(interval)
            awslogger.log_info(f"Verify code not found, retrying {5 - retry}")
    return messages[-1]


