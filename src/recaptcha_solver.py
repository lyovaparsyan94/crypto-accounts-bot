from twocaptcha import TwoCaptcha
from configs.constants import CAPTCHA_API_KEY


class CaptchaSolver:
    def __init__(self):
        self.__api_key = CAPTCHA_API_KEY
        self.solver = TwoCaptcha(self.__api_key)

    def get_captcha_code(self, image_src: str) -> str:
        """
        Gets the captcha code from the provided image source (image_src)
        Returns:
            str: The captcha code.
        """
        captcha_code = self.solver.normal(image_src)
        return captcha_code['code']