import os
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.by import By

load_dotenv()


class CaptchaSolver:
    def __init__(self):
        self.api_key = os.getenv('CAPTCHA_API_KEY')
        self.solver = TwoCaptcha(self.api_key)

    def get_captcha_code(self, image_src):
        captcha_code = self.solver.normal(image_src)
        return captcha_code['code']
