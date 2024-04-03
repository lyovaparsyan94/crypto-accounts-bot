import os
from os.path import join

from pydantic import BaseSettings

BASE_DIR = os.path.abspath(__file__)
project_dir = os.path.dirname(os.path.dirname(BASE_DIR))
ENV_DIR = join(project_dir, '.env')


class PrivateConfigs(BaseSettings):
    CVV: str | None
    EXPIRE_DATE: str | None
    CARD_NUMBER: str | None
    CARDHOLDER: str | None
    CAPTCHA_API_KEY: str | None
    SIM_API_TOKEN: str | None


class DirConfigs(BaseSettings):
    AWS_FILENAME = "aws_data.json"
    CURRENT_SIM_INFO = "current_sim.json"
    SRC_DIR = os.path.dirname(BASE_DIR)
    DATA_DIR = join(SRC_DIR, join('data'))
    LOGS_DIR = join(SRC_DIR, join('logs'))
    LOG_FILE = join(LOGS_DIR, 'aws_logs.log')
    LOG_CONFIG_FILE = join(LOGS_DIR, 'logging.yaml')
    PATH_TO_SAVE = os.path.join(DATA_DIR, AWS_FILENAME)
    PATH_OF_SIM_JSON = os.path.join(DATA_DIR, CURRENT_SIM_INFO)


class AwsSettings(BaseSettings):
    MANDATORY_FIELDS = ['cards', 'emails', 'phones']
    REQUIRED_FIELDS = ['first_name', 'last_name', 'card_number', 'valid_date', 'cvv', 'cardholder', "phone",
                       'full_name',
                       'email', 'root_pass',
                       'account_name', 'verify_email_code', "city", "postal_code", "country", "full_address", "card"]
    URL = "https://portal.aws.amazon.com/billing/signup#/identityverification"
    ONLINE_COUNTRY_CODE: str = '46'
    ONLINE_SIM_SERVICE: str = 'Amazon'
    PHONE_LIMIT = 9
    CARD_LIMIT = 9
    EMAIL_LIMIT = 9


class SubSettings(BaseSettings):
    sub_field: str | None
    # dir_configs = DirConfigs()


class Config(BaseSettings):
    sub_settings: SubSettings
    private_configs: PrivateConfigs
    aws_configs: AwsSettings()
    dir_configs = DirConfigs()

    def __init__(self, *args, **kwargs):
        kwargs['sub_settings'] = SubSettings(_env_file=kwargs['_env_file'])
        kwargs['private_configs'] = PrivateConfigs(_env_file=kwargs['_env_file'])
        kwargs['aws_configs'] = AwsSettings()
        super().__init__(*args, **kwargs)


configs = Config(_env_file=ENV_DIR)
