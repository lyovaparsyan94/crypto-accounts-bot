from aws_scrapper import AwsRegistrator
from helpers.temp_mail import generate_mail  # noqa


def main():
    # aws = AwsRegistrator(email=generate_mail()) # use to generate random temporary onetime mail (for tests)
    aws = AwsRegistrator('your@email.com', 'your_imap_password')
    aws.register()


if __name__ == '__main__':
    main()
