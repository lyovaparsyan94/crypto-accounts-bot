from aws_scrapper import AwsRegistrator
from logs.aws_logger import awslogger
from utils.temp_mail import generate_mail  # noqa


def main() -> None:
    """
    Creates an AwsRegistrator instance using the provided email and password.

    Args:
        None

    Returns:
        None
    """
    try:
        aws = AwsRegistrator(email=generate_mail())  # use to generate random temporary onetime mail (for tests)
        # aws = AwsRegistrator('yourmail_example@gmx.com', 'your_password_')
        aws.register()
    except BaseException as e:
        awslogger.log_critical(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
