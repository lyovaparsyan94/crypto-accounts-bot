import os
from os.path import join
from dotenv import load_dotenv

load_dotenv()
CAPTCHA_API_KEY = '81d0c80606eb7773b4dbc170fa309a61'
ONLINE_COUNTRY_CODE = '1'
ONLINE_SIM_SERVICE = 'Amazon'

USER_DATA_DIR = os.getenv('USER_DATA_DIR')

file_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(file_path)
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = join(ROOT_DIR, join('data'))
LOGS_DIR = join(ROOT_DIR, join('logs'))

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
