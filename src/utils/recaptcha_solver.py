from selenium.webdriver.chrome.webdriver import WebDriver
from twocaptcha import TwoCaptcha


class CaptchaSolver:
    def __init__(self, driver: WebDriver, captcha_key: str) -> None:
        """
        Initialize a CaptchaSolver instance.

        Args:
            driver (WebDriver): The Selenium WebDriver instance.
        """
        self.solver = TwoCaptcha(apiKey=captcha_key)
        self.driver = driver

    def get_captcha_code(self, image_src: str) -> str:
        """
        Gets the captcha code from the provided image source.

        Args:
            image_src (str): The URL of the captcha image.

        Returns:
            str: The captcha code.
        """
        captcha_code = self.solver.normal(image_src)
        return captcha_code['code']
