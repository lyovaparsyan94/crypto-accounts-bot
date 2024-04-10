from aws_scrapper import AwsRegistrator
from logs.aws_logger import awslogger
from utils.temp_mail import generate_mail  # noqa

from tests.usecases import test_steps


def main() -> None:
    """
    Creates an AwsRegistrator instance using the provided email and password.
    Making registration 20 times

    Args:
        None

    Returns:
        None
    """
    counter = 1
    try:
        for _ in range(20):
            aws = AwsRegistrator(email=generate_mail())
            # aws = AwsRegistrator('yourmail_example@gmx.com', 'your_password_')
            test_steps(aws_instance=aws)
            awslogger.log_info(f'made registration {counter} times')
            counter += 1
    except Exception as e:
        awslogger.log_critical(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
