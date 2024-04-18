from aws_scrapper import AwsRegistrator
from logs.aws_logger import awslogger
from utils.temp_mail import generate_mail  # noqa
from config import configs


def main() -> None:
    """
    Creates an AwsRegistrator instance using the provided email and password.

    Args:
        None

    Returns:
        None
    """
    try:
        MAIL = configs.private_configs.MAIL
        IMAP_MAIL_PASSWORD = configs.private_configs.IMAP_MAIL_PASSWORD
        # aws = AwsRegistrator(email=generate_mail()) # use to generate random temporary onetime mail (for tests)
        aws = AwsRegistrator(MAIL, IMAP_MAIL_PASSWORD)
        aws.register()
        awslogger.log_info("AWS instances created")
    except BaseException as e:
        awslogger.log_critical(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
