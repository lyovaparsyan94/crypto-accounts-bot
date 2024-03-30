from traceback import print_stack

from aws_scrapper import AwsRegistrator
from helpers.temp_mail import generate_mail  # noqa


def main():
    try:
        # aws = AwsRegistrator(email=generate_mail()) # use to generate random temporary onetime mail (for tests)
        aws = AwsRegistrator('alex.smith@examplea.com', 'your@email.com')
        aws.register()
    except BaseException as e:
        print(f"\nError creating AWS instance: {e}\n")


if __name__ == '__main__':
    main()
