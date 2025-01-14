from collections.abc import Callable
from time import sleep
from typing import Any

from config import configs
from logs.aws_logger import awslogger
from selenium.common import (
    ElementNotSelectableException,
    ElementNotVisibleException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import WebElement
from utils.recaptcha_solver import CaptchaSolver


class ElementHandler:
    def __init__(self, driver: WebElement) -> None:
        """
        Initialize an ElementHandler instance.

        Args:
            driver: The Selenium WebDriver instance.
        """
        self.driver = driver
        self.captcha_solver = CaptchaSolver(driver=self.driver, captcha_key=configs.private_configs.CAPTCHA_API_KEY)

    def wait_for_element(self, locator: str, by_type: str = By.XPATH, timeout: int = 30, poll_frequency: float = 0.5,
                         name: str = '') -> WebElement:
        """
        Wait for an element to become visible.

        Args:
            locator (str): The locator string (e.g., XPath) of the element.
            by_type (str, optional): The type of locator (default is By.XPATH).
            timeout (int, optional): Maximum time to wait for the element (default is 30 seconds).
            poll_frequency (float, optional): Polling frequency (default is 0.5 seconds).
            name (str, optional): Name of the element for logging purposes.

        Returns:
            WebElement: The located element.
        """
        element = None
        self.driver.implicitly_wait(0)
        try:
            wait = WebDriverWait(self.driver, timeout=timeout, ignored_exceptions=[
                NoSuchElementException,
                ElementNotVisibleException, StaleElementReferenceException,
                ElementNotSelectableException])
            element = wait.until(EC.visibility_of_element_located((by_type, locator)))
        except Exception:
            awslogger.log_warning(f"Element {name} NOT appeared ")
        return element

    def is_element_present(self, locator: str, by_type: By = By.XPATH, name: str = '') -> bool:
        """
        Check if an element is present on the page.

        Args:
            locator (str): The locator string (e.g., XPath) of the element.
            by_type (str, optional): The type of locator (default is 'xpath').
            name (str, optional): Name of the element for logging purposes.

        Returns:
            bool: True if the element is present, False otherwise.
        """
        try:
            element = self.driver.find_element(by_type, locator)
            if element is not None:
                return True
            return False
        except NoSuchElementException:
            awslogger.log_warning(f"Element {name} not found {name}, reason: maybe you are using test emails")
            return False
        except Exception:
            awslogger.log_warning(f"Unknown error {name}")
            return False

    def is_shown_warning(self, warning_xpath: str = '', name: str = None) -> bool:
        """
        Check if a warning element is displayed.

        Args:
            warning_xpath (str, optional): The XPath of the warning element (default is '').
            name (str, optional): Name of the warning element for logging purposes.

        Returns:
            bool: True if the warning element is displayed, False otherwise.
        """
        if warning_xpath is None:
            return True
        try:
            element = self.driver.find_element(By.XPATH, warning_xpath)
            if element.is_displayed():
                return True
            return False
        except Exception:
            awslogger.log_info(f"warning '{name}' not shown")
            return False

    def slow_input(self, input_field: WebElement, sequence: str) -> None:
        """
        Slowly inputs a sequence of characters into an input field.

        Args:
            input_field (Any): The input field element (e.g., a web element or input field object).
            sequence (str): The sequence of characters to input.

        Returns:
            None

        Notes:
            - This method simulates human-like typing by adding a delay between each character input.
            - Useful for testing or scenarios where realistic user input timing is required.
        """
        for symbol in sequence:
            input_field.send_keys(symbol)
            sleep(0.10)
        awslogger.log_info(f'filled {sequence} in input field')

    @staticmethod
    def wait_for_result(func: Callable[..., Any], period: int = 60, interval: int = 3) -> Callable[..., Any]:
        """
        Decorator that waits for a result from the given function.

        Args:
            func (Callable[..., Any]): The function to be wrapped.
            period (int, optional): Total waiting time in seconds. Defaults to 60.
            interval (int, optional): Time between retries in seconds. Defaults to 3.

        Returns:
            Callable[..., Any]: The wrapped function with retry logic.
        """

        def wrapper(self, *args, **kwargs) -> Any:
            """
            Wrapper function that adds retry logic to the original function.

            Args:
                self: Instance of the class.
                *args: Positional arguments for the original function.
                **kwargs: Keyword arguments for the original function.

            Returns:
                Any: Result of the original function or None if timed out.
            """
            for _ in range(period):
                awslogger.log_info(f"waiting for message from: {func.__name__}")
                result = func(self, *args, **kwargs)
                if result:
                    awslogger.log_info(f"function {func.__name__} completed with result: {result}")
                    return result
                sleep(interval)
            awslogger.log_critical(f"Timed out waiting for {func.__name__}")

        return wrapper

    def try_solve_captcha(self, xpath: str, retry: int = 5, interval: int = 3) -> None:
        """
        Attempt to solve a captcha using the provided XPath.

        Args:
            xpath (str): The XPath of the captcha element.
            retry (int, optional): Number of retry attempts (default is 5).
            interval (int, optional): Interval between retries (default is 3 seconds).

        Returns:
            None
        """
        awslogger.log_info('trying to solve captcha')
        warning1 = True
        warning2 = True
        while (retry >= 1 and warning1 is not None) or (retry >= 1 and warning2 is not None):
            try:
                self.captcha_resolve(xpath=xpath)
            except BaseException:
                retry -= 1
                sleep(interval)
            finally:
                warning1 = self.wait_for_element(locator="//a[@href='https://aws.amazon.com/support/createCase']",
                                                 name='warning captcha 1', timeout=3)
                warning2 = self.wait_for_element(
                    locator="//form[@id='IdentityVerification']//div[contains(text(), 'Security check characters are incorrect. Please try again.')]",
                    name='warning captcha 2', timeout=3)

    def captcha_resolve(self, xpath: str) -> None:
        """
        Resolve a captcha using the provided XPath.

        Args:
            xpath (str): The XPath of the captcha element.

        Returns:
            None
        """
        image = self.driver.find_element(By.XPATH, xpath)
        image_src = image.get_attribute('src')
        captcha_code = self.captcha_solver.get_captcha_code(image_src=image_src)
        awslogger.log_info(f'captcha code: {captcha_code}')
        input_captcha = self.driver.find_element(By.XPATH, "//*[@id='captchaGuess'] //input[@name='captchaGuess']")
        self.slow_input(input_captcha, captcha_code)
