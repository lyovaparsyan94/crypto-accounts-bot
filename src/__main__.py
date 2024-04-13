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
        for i in range(9, 205):
            # aws = AwsRegistrator(f'levaparsyan+{i}@dot-agency.net', 'gjdl cwfg hqko vmwu')
            # aws.register()
            print()
    except BaseException as e:
        awslogger.log_critical(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
