import os
from os.path import join

file_path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(file_path)
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = join(ROOT_DIR, join('data'))
LOGS_DIR = join(ROOT_DIR, join('logs'))

URL = "https://www.akamai.com/create-account"
COOKIES_ID = "onetrust-accept-btn-handler"
EMAIL_ID = "BizEmail"
USER_NAME_ID = "BizUsername"
PASSWORD_ID = "BizPassword"
SUBMIT_FIRST_XPATH = "//button[@class='o-button']"

TELS_ID = 'iso_code'
CAPTCHA_API_KEY = '81d0c80606eb7773b4dbc170fa309a61'