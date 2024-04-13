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
        for i in range(1, 201):
            # aws = AwsRegistrator(email=generate_mail()) # use to generate random temporary onetime mail (for tests)
            aws = AwsRegistrator('exmaple@gmx.com', 'gmxemail_password')
            aws.register()
            awslogger.log_info(f"{i} AWS instances created")
    except BaseException as e:
        awslogger.log_critical(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
