from time import sleep

from helpers.recaptcha_solver import CaptchaSolver
from selenium.common import ElementNotSelectableException, ElementNotVisibleException, NoSuchElementException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ElementHandler:
    def __init__(self, driver):
        self.driver = driver
        self.captcha_solver = CaptchaSolver(driver=self.driver)

    def wait_for_element(self, locator, by_type=By.XPATH, timeout=30, poll_frequency=0.5, name=''):
        element = None
        self.driver.implicitly_wait(0)
        try:
            wait = WebDriverWait(self.driver, timeout=timeout, ignored_exceptions=[
                NoSuchElementException,
                ElementNotVisibleException, StaleElementReferenceException,
                ElementNotSelectableException])
            element = wait.until(EC.visibility_of_element_located((by_type, locator)))
        except Exception:
            print(f"Element {name} NOT appeared ")
        return element

    def is_element_present(self, locator: str, by_type: str = 'xpath', name: str = '') -> bool:
        try:
            element = self.driver.find_element(by_type, locator)
            if element is not None:
                return True
            return False
        except NoSuchElementException:
            print(f"Element {name} with type {by_type} not found {name}")
            return False
        except Exception:
            print(f"Unknown Error {name}")
            return False

    def is_shown_warning(self, warning_xpath: str = '', name: str = None) -> bool:
        if warning_xpath is None:
            return True
        try:
            element = self.driver.find_element(By.XPATH, warning_xpath)
            if element.is_displayed():
                return True
            return False
        except Exception:
            print(f"The warning element '{name}' not shown")
            return False

    def slow_input(self, field_to_fill, sequence):
        for symbol in sequence:
            field_to_fill.send_keys(symbol)
            # sleep(choice([0.70, 0.91, 0.83, 0.55, 0.41, 0.63, 0.15, 0.21, 0.33]))
            sleep(0.10)

    def try_solve_captcha(self, xpath, retry=5, interval=3):
        print('trying to solve captcha')
        warning1 = True
        warning2 = True
        while (retry >= 1 and warning1) or (retry >= 1 and warning2):
            try:
                self.captcha_resolve(xpath=xpath)
            except BaseException:
                retry -= 1
                sleep(interval)
            finally:
                warning1 = self.wait_for_element(locator="//a[@href='https://aws.amazon.com/support/createCase']", timeout=2)
                warning2 = self.wait_for_element(locator="//form[@id='IdentityVerification']//div[contains(text(), 'Security check characters are incorrect. Please try again.')]", timeout=2)

    def captcha_resolve(self, xpath):
        image = self.driver.find_element(By.XPATH, xpath)
        image_src = image.get_attribute('src')
        captcha_code = self.captcha_solver.get_captcha_code(image_src=image_src)
        print(f'captcha code: {captcha_code}')
        input_captcha = self.driver.find_element(By.XPATH, "//*[@id='captchaGuess'] //input[@name='captchaGuess']")
        self.slow_input(input_captcha, captcha_code)
