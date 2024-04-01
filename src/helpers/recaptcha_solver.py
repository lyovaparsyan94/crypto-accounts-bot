from config import configs
from twocaptcha import TwoCaptcha

# from configs import CAPTCHA_API_KEY

CAPTCHA_API_KEY = configs.private_configs.CAPTCHA_API_KEY

class CaptchaSolver:
    def __init__(self, driver):
        self.__api_key = CAPTCHA_API_KEY
        self.solver = TwoCaptcha(self.__api_key)
        self.driver = driver

    def get_captcha_code(self, image_src: str) -> str:
        """
        Gets the captcha code from the provided image source (image_src)
        Returns:
            str: The captcha code.
        """
        captcha_code = self.solver.normal(image_src)
        return captcha_code['code']
