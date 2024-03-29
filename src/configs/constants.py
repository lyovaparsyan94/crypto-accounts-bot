import os
from os.path import join

from dotenv import load_dotenv

load_dotenv()

CVV = os.getenv('CVV')
EXPIRE_DATE = os.getenv('EXPIRE_DATE')
CARD_NUMBER = os.getenv('CARD_NUMBER')
CARDHOLDER = os.getenv('CARDHOLDER')

CAPTCHA_API_KEY = os.getenv('CAPTCHA_API_KEY')
SIM_API_TOKEN = os.getenv('SIM_API_TOKEN')

ONLINE_COUNTRY_CODE = '46'
ONLINE_SIM_SERVICE = 'Amazon'

USER_DATA_DIR = os.getenv('USER_DATA_DIR')

file_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(file_path)
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = join(ROOT_DIR, join('data'))
LOGS_DIR = join(ROOT_DIR, join('logs'))
print(BASE_DIR)

URL = "https://portal.aws.amazon.com/billing/signup#/identityverification"
AWS_FILENAME = "aws_data.json"
TELS_ID = 'iso_code'
PATH_TO_SAVE = os.path.join(DATA_DIR, AWS_FILENAME)

PHONE_LIMIT = 9
CARD_LIMIT = 9
EMAIL_LIMIT = 9

MANDATORY_FIELDS = ['cards', 'emails', 'phones']
REQUIRED_FIELDS = ['first_name', 'last_name', 'card_number', 'valid_date', 'cvv', 'cardholder', "phone", 'full_name',
                   'email', 'root_pass',
                   'account_name', 'verify_email_code', "city", "postal_code", "country", "full_address", "card"]
