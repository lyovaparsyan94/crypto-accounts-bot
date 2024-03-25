import os
from os.path import join

file_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(file_path)
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = join(ROOT_DIR, join('data'))
LOGS_DIR = join(ROOT_DIR, join('logs'))

URL = "https://www.akamai.com/create-account"
AWS_FILENAME = "aws_data"
TELS_ID = 'iso_code'

PHONE_LIMIT = 9
CARD_LIMIT = 9
EMAIL_LIMIT = 9



