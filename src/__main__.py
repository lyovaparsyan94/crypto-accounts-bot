
from aws_scrapper  import AwsRegistrator
from helpers.temp_mail import generate_mail

if __name__ == '__main__':
    # aws = AwsRegistrator("martinezvgz12is@gmail.com", 'ytlf iyds vvsh hzid')
    # aws = AwsRegistrator("5jffivhb@duck.com", 'pwol xyab lesl suph')
    aws = AwsRegistrator(email=generate_mail())
    aws.register()
