import time
import random
from selenium import webdriver
from traceback import print_stack
from imap_handler import ImapHandler
import undetected_chromedriver as uc
from recaptcha_solver import CaptchaSolver
from configs.constants import USER_DATA_DIR
from selenium.webdriver.common.by import By
from helpers.file_handler import FileHandler
from helpers.randomizer import generate_root_name
from selenium.webdriver.support.ui import WebDriverWait
from helpers.temp_mail import check_last_message, generate_mail
from selenium.webdriver.support import expected_conditions as EC
from helpers.phone_identifier import get_country_code, get_national_number
from selenium.common import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException


class AwsRegistrator:
    def __init__(self, email=None, password=None):
        self.user_info = None
        self.options = uc.ChromeOptions()
        # self.options.add_argument("--proxy-server=171.243.3.55:4006")
        self.options.add_argument(rf'--user-data-dir={USER_DATA_DIR}')
        # self.driver = webdriver.Chrome()
        self.driver = uc.Chrome(options=self.options)
        self.solver = CaptchaSolver()
        self.file_handler = FileHandler()
        self.email = email
        self.password = password
        self.account_name = email[0:-4].capitalize()
        self.tell_number = "+37477970340"
        self.first_name = "Pau"
        self.last_name = "Storer"
        self.full_name = f"{self.first_name} {self.last_name}"
        self.cardholder_name = "Pau Storer"
        self.bank_number = "4278627431140307"
        self.valid_date = "08/25"
        self.cvv = "678"
        self.city = 'Yerevan'
        self.state = ' '
        self.postal_code = '0065'
        self.country = 'Armenia'
        # self.address = f'1913 Belleau Dr, {self.city}, {self.state} {self.postal_code}, USA'
        self.address = f'10 Sebastia St, {self.city}, {self.state} {self.postal_code}, {self.country}'
        self.url = "https://portal.aws.amazon.com/billing/signup#/identityverification"
        if password:
            self.imap_instance = ImapHandler(self.email, self.password)

    def open_page(self):
        self.driver.maximize_window()
        # self.driver.get('https://browserleaks.com/ip')
        self.driver.get(self.url)
        self.driver.implicitly_wait(5)

    def step_one(self, email=None, retry=5, interval=5):
        print('--started step one')
        warning_email = True
        time.sleep(3)
        while retry >= 1 and warning_email:
            try:
                self.email_confirm(email=email)
            except BaseException as e:
                retry -= 1
                time.sleep(interval)
                retry -= 5
                print(f"Confirming email {5 - retry} time")
            finally:
                warning_email = self.is_shown_warning(warning_xpath='//*[@id="awsui-input-0"]', name='email warning')
                print(f"Email confirmed")

    def email_confirm(self, email=None):
        root_email = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-0"]')
        root_email.clear()
        if email is None:
            self.slow_input(root_email, self.email)
        else:
            email = generate_mail()
        time.sleep(1)
        acc_name = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-1"]')
        self.slow_input(acc_name, self.account_name)
        verify_email = self.driver.find_element(By.XPATH,
                                                '//*[@id="EmailValidationSendOTP"]/fieldset/awsui-button[1]/button')
        verify_email.click()

    def step_two(self):
        print('--started step two')
        time.sleep(3)
        confirm_mail = self.driver.find_element(By.XPATH, "//awsui-input[@id='otp']/div/input[@name='otp']")
        confirm_mail.clear()
        if self.password:
            verify_code = self.imap_instance.mailbox_confirm_message()
        else:
            verify_code = check_last_message(self.email)
            if not verify_code:
                not_you_button = self.driver.find_element(By.XPATH,
                                                          "//*[@id='EmailValidationVerifyOTP']/fieldset/p/span[contains(text(), 'not you')]")
                not_you_button.click()
                print('generating new  email and get new code')
                time.sleep(2)
                self.step_one()

        self.slow_input(confirm_mail, sequence=verify_code)
        verify_button = self.driver.find_element(By.XPATH,
                                                 '//*[@id="EmailValidationVerifyOTP"]/fieldset/awsui-button[1]/button')
        time.sleep(2)
        verify_button.click()

    def step_three(self, retry=8, interval=5):
        print('--started step three')
        warning_shown = True
        while retry >= 1 and warning_shown:
            try:
                self.root_confirm()
            except BaseException:
                time.sleep(interval)
                retry -= 1
                time.sleep(interval)
            finally:
                warning_shown = self.is_shown_warning(
                    "//a[@href='https://support.aws.amazon.com/#/contacts/aws-account-support']", name='root')
                if not warning_shown:
                    print('confirmed root pass')

    def root_confirm(self):
        root = generate_root_name()
        time.sleep(2)
        root_field1 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-3"]')
        root_field1.clear()
        self.slow_input(root_field1, sequence=root)
        root_field2 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-4"]')
        root_field2.clear()
        self.slow_input(root_field2, sequence=root)
        verify = self.driver.find_element(By.XPATH,
                                          "//*[@id='CredentialCollection']/fieldset/awsui-button[1]/button[span[text()='Continue (step 1 of 5)']]")
        time.sleep(3)
        try:
            need_captcha = self.driver.find_element(By.XPATH, '//div[contains(@class, "Captcha_mainDisplay")]')
            if need_captcha and need_captcha.is_displayed():
                print('need captcha:', need_captcha and need_captcha.is_displayed())
                time.sleep(3)
                self.captcha_resolve(xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
        except NoSuchElementException:
            print('Not captcha shown')
        verify.click()

    def step_four(self):
        print('--started step four')
        personal = self.driver.find_element(By.XPATH, '//*[@id="awsui-radio-button-2"]')
        personal.click()
        time.sleep(1)

        full_name_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-5"]')
        self.slow_input(full_name_field, self.full_name)
        time.sleep(1)

        region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-1"]')
        region.click()
        time.sleep(1)
        country_select = self.driver.find_element(By.XPATH,
                                                  f"//div[contains(@data-value, '{get_country_code(self.tell_number)}')]")
        country_select.click()
        time.sleep(1)

        phone_field = self.driver.find_element(By.XPATH, '//input[@name="address.phoneNumber"]')
        self.slow_input(phone_field, get_national_number(self.tell_number))
        time.sleep(1)

        country_or_region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-2"]')
        country_or_region.click()
        found_county = self.driver.find_element(By.XPATH,
                                                f"//div[contains(@data-value, '{get_country_code(self.tell_number)}') and contains(@class, 'awsui-select-option-selectable')]")
        found_county.click()
        time.sleep(1)
        address_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-9"]')
        self.slow_input(address_field, self.address)
        time.sleep(1)

        city = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-11"]')
        self.slow_input(city, self.city)
        time.sleep(1)

        state_region_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-12"]')
        self.slow_input(state_region_field, self.state)
        time.sleep(1)

        postal_code = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-13"]')
        self.slow_input(postal_code, self.postal_code)
        time.sleep(1)

        agree_checkbox = self.driver.find_element(By.XPATH, '//*[@id="awsui-checkbox-0"]')
        agree_checkbox.click()

        continue_button = self.driver.find_element(By.XPATH,
                                                   '//*[@id="ContactInformation"]/fieldset/awsui-button/button')
        time.sleep(1)
        continue_button.click()

    def step_five(self):
        print('--started step five')
        time.sleep(3)
        card_number_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-14"]')
        self.slow_input(card_number_field, self.bank_number)

        mouth_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-3"]')
        mouth_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[:2]}']")
        mouth.click()
        time.sleep(2)

        year_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-4"]')
        year_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='20{self.valid_date[3:]}']")
        mouth.click()
        time.sleep(1)

        cvv_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-15"]')
        self.slow_input(cvv_field, self.cvv)
        time.sleep(1)

        cardholder_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-16"]')
        self.slow_input(cardholder_field, self.cardholder_name)
        time.sleep(2)

        verify_step = self.driver.find_element(By.XPATH, '//*[@id="PaymentInformation"]/fieldset/awsui-button/button')
        verify_step.click()
        time.sleep(5)

    def step_six(self):
        print('--started step six')
        country_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-5"]')
        country_field.click()
        time.sleep(2)

        region = get_country_code(self.tell_number)
        mouth = self.driver.find_element(By.XPATH, f"//div[contains(@data-value, '{region}')]")
        mouth.click()
        time.sleep(2)

        national_number_field = self.driver.find_element(By.XPATH, '//*[@id="phoneNumber"]/div/input')
        national_number = get_national_number(self.tell_number)
        print(f'national number: {national_number}')
        self.slow_input(national_number_field, national_number)
        time.sleep(4)

    def step_seven(self, retry=5, interval=3):
        print("--started step seven")
        warning1 = True
        warning2 = True
        while (retry >= 1 and warning1) or (retry >= 1 and warning2):
            try:
                self.captcha_resolve(xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
                verify = self.driver.find_element(By.XPATH, "//button[span[text()='Send SMS (step 4 of 5)']]")
                verify.click()
            except BaseException:
                time.sleep(2)
                retry -= 1
                time.sleep(interval)
                print(f"Solving captcha {5 - retry} times after {interval} sec interval")
            finally:
                warning1 = self.is_shown_warning(warning_xpath="//a[@href='https://aws.amazon.com/support/createCase']",
                                                 name='captcha1')
                warning2 = self.is_shown_warning(
                    warning_xpath="//form[@id='IdentityVerification']//div[contains(text(), 'Security check characters are incorrect. Please try again.')]",
                    name='captcha2')

    def captcha_resolve(self, xpath):
        image = self.driver.find_element(By.XPATH, xpath)
        image_src = image.get_attribute('src')
        captcha_code = self.solver.get_captcha_code(image_src=image_src)
        print(f'captcha code: {captcha_code}')
        input_captcha = self.driver.find_element(By.XPATH, "//*[@id='captchaGuess'] //input[@name='captchaGuess']")
        self.slow_input(input_captcha, captcha_code)

    @staticmethod
    def slow_input(field_to_fill, sequence):
        for symbol in sequence:
            field_to_fill.send_keys(symbol)
            time.sleep(random.choice([0.70, 0.91, 0.83, 0.55, 0.41, 0.63, 0.15, 0.21, 0.33]))
            # time.sleep(0.03)

    def is_shown_warning(self, warning_xpath: str = '', name: str = None):
        if warning_xpath is None:
            return True
        try:
            element = self.driver.find_element(By.XPATH, warning_xpath)
            if element.is_displayed():
                return True
            else:
                return False
        except NoSuchElementException:
            print(f"The warning element '{name}' not shown on the page.")
            return False

    def is_element_present(self, by_type, locator):
        try:
            element = self.driver.find_element(by_type, locator)
            if element is not None:
                print('Element found')
                return True
            else:
                return False
        except NoSuchElementException:
            print(f"Element {locator} with type {by_type} not found")
            return False
        except Exception as e:
            print(f"Unknown Error {e}")
            return False

    def wait_for_element(self, locator, by_type='xpath', timeout=30, poll_frequency=0.5):
        element = None
        try:
            self.driver.implicitly_wait(0)
            print(f"Waiting for maximum ---{str(timeout)} ---- seconds for element to be clickable")
            wait = WebDriverWait(self.driver, timeout=timeout, poll_frequency=poll_frequency, ignored_exceptions=[
                NoSuchElementException,
                ElementNotVisibleException,
                ElementNotSelectableException])
            element = wait.until(EC.visibility_of_element_located((by_type, locator)))
            print("Element appeared on the web page")
        except:
            print("Element NOT appeared on the web page")
            print_stack()
            self.driver.implicitly_wait(2)
        return element

    def register(self):
        """Registers an AWS account by completing the required steps."""  # TODO need finish registation steps, when will be ready all components
        self.open_page()                                                  # TODO and made all tests
        self.step_one()
        self.step_two()
        self.step_three()
        self.step_four()
        self.step_five()
        self.step_six()
        self.step_seven()
        time.sleep(32)


