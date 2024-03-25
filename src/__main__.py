from aws_scrapper  import AwsRegistrator
from helpers.temp_mail import generate_mail

if __name__ == '__main__':
    aws = AwsRegistrator(email=generate_mail())
    aws.register()
