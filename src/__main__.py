
from aws_scrapper import AwsRegistrator
from helpers.temp_mail import generate_mail


def main():
    # aws = AwsRegistrator(email=generate_mail())
    aws = AwsRegistrator("sepanezugiwz@gmx.com", "sbOYHDeQIA")
    aws.register()


if __name__ == '__main__':
    main()
