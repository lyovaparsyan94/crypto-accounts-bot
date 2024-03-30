from aws_scrapper import AwsRegistrator
from helpers.temp_mail import generate_mail  # noqa


def main() -> None:
    """
    Creates an AWS instance using the provided email and password.

    Args:
        None

    Returns:
        None
    """
    try:
        # aws = AwsRegistrator(email=generate_mail()) # use to generate random temporary onetime mail (for tests)
        aws = AwsRegistrator('your_gmail@examplea.com', 'your_password')
        aws.register()
    except BaseException as e:
        print(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
