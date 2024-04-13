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
            aws = AwsRegistrator(f'email+{i}@example.com', 'your_password')
            aws.register()
            print()
    except BaseException as e:
        awslogger.log_critical(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
