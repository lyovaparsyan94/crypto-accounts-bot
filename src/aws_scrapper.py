import time
import random
from selenium import webdriver
from traceback import print_stack
from imap_handler import ImapHandler
import undetected_chromedriver as uc
from recaptcha_solver import CaptchaSolver
from selenium.webdriver.common.by import By
from helpers.file_handler import FileHandler
from helpers.randomizer import generate_root_name, generate_first_last_name, generate_cardholder_name, \
    generate_card_data as card_data, generate_random_addresses as addresses
from selenium.webdriver.support.ui import WebDriverWait
from helpers.temp_mail import check_last_message, generate_mail
from selenium.webdriver.support import expected_conditions as EC
from helpers.phone_identifier import get_country_code, get_national_number
from selenium.common import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException


class AwsRegistrator:
    def __init__(self, email=None, password=None):
        self.options = uc.ChromeOptions()
        self.file_handler = FileHandler()
        self.user_created = False
        # self.options.add_argument("--proxy-server=159.203.61.169:3128")
        # self.options.add_argument(rf'--user-data-dir={USER_DATA_DIR}')
        # self.options.add_argument(r'--user-data-dir=C:\Users\parsy\AppData\Local\Google\Chrome\User Data\Profile')
        # self.driver = webdriver.Chrome()
        self.driver = uc.Chrome(options=self.options)
        self.solver = CaptchaSolver()
        self.email = email
        self.root_name = None
        self.password = password
        self.verify_email_code = None
        self.account_name = email[0:-4].capitalize()
        self.phone = "+37477970340"
        self.first_name, self.last_name = generate_first_last_name()
        self.full_name = f"{self.first_name} {self.last_name}"
        self.cardholder_name = generate_cardholder_name()
        self.card, self.cvv, self.valid_date = card_data()['card_number'], card_data()['cvv'], card_data()[
            'expiry_date']
        self.address, self.city, self.state, self.postal_code, self.country, self.full_address = addresses().values()
        self.url = "https://portal.aws.amazon.com/billing/signup#/identityverification"
        if password:
            self.imap_instance = ImapHandler(self.email, self.password)

    def open_page(self):
        self.driver.maximize_window()
        self.driver.get(self.url)
        self.driver.implicitly_wait(5)

    def step_one(self, email=None, retry=5, interval=5):
        warning_email = True
        while retry >= 1 and warning_email:
            try:
                self.email_confirm()
            except NoSuchElementException as e:
                retry -= 1
                time.sleep(interval)
                retry -= 5
                print(f"Confirming email {5 - retry} time")
            finally:
                warning_email = self.is_shown_warning(warning_xpath='//*[@id="awsui-input-0"]', name='email warning')

    def email_confirm(self, email=None):
        # root_email_field = self.wait_for_element(locator='//*[@id="awsui-input-0"]')
        root_email_field = self.wait_for_element(locator="//div//input[@name='emailAddress']")
        while not self.is_element_present(locator="//div//input[@name='emailAddress']"):
            time.sleep(1)
        else:
            root_email_field.clear()
        if email is None:
            self.slow_input(root_email_field, self.email)
        else:
            email = generate_mail()
            self.email = email
        time.sleep(1)
        # acc_name = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-1"]')
        acc_name_field = self.wait_for_element(locator="//div//input[@name='fullName']")
        while not self.is_element_present(locator="//div//input[@name='fullName']"):
            time.sleep(1)
        else:
            acc_name_field.clear()
        self.account_name = self.email[0:-4].capitalize()
        self.slow_input(acc_name_field, self.account_name)
        verify_email = self.driver.find_element(By.XPATH,
                                                '//*[@id="EmailValidationSendOTP"]/fieldset/awsui-button[1]/button')
        verify_email.click()
        time.sleep(3)
        return email

    def step_two(self):
        while not self.wait_for_element("//awsui-input[@id='otp']/div/input[@name='otp']"):
            time.sleep(1)
        else:
            confirm_mail = self.driver.find_element(By.XPATH, "//awsui-input[@id='otp']/div/input[@name='otp']")
            confirm_mail.clear()
            if self.password:
                verify_code = self.imap_instance.mailbox_confirm_message()
            else:
                verify_code = check_last_message(self.email)
            if verify_code:
                verify_button = self.driver.find_element(By.XPATH,
                                                         '//*[@id="EmailValidationVerifyOTP"]/fieldset/awsui-button[1]/button')
                self.slow_input(confirm_mail, sequence=verify_code)
                self.verify_email_code = verify_code
                verify_button.click()
            while not verify_code:
                not_you_button = self.driver.find_element(By.XPATH,
                                                          "//*[@id='EmailValidationVerifyOTP']/fieldset/p/span[contains(text(), 'not you')]")
                not_you_button.click()
                self.step_one()

    def step_three(self, retry=15, interval=4):
        time.sleep(2)
        root_name = False
        warning_shown = True
        # verify_button = self.wait_for_element(By.XPATH,
        #                                       "//*[@id='CredentialCollection']/fieldset/awsui-button[1]/button[span[text()='Continue (step 1 of 5)']]")
        verify_button = self.driver.find_element(By.XPATH,
                                                 "//*[@id='CredentialCollection']/fieldset/awsui-button[1]/button[span[text()='Continue (step 1 of 5)']]")
        while not self.root_name and warning_shown:
            try:
                temp_root_name = self.root_confirm()
                verify_button.click()
            except BaseException:
                time.sleep(interval)
                retry -= 1
                time.sleep(interval)
            finally:
                time.sleep(2)
                warning_shown = self.is_element_present(
                    locator="//a[@href='https://support.aws.amazon.com/#/contacts/aws-account-support']")
                if not warning_shown and temp_root_name:
                    captcha_shown = self.is_element_present(locator='//div[contains(@class, "Captcha_mainDisplay")]',
                                                            name='captcha')
                    while captcha_shown:
                        try:
                            self.captcha_resolve(
                                xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
                            captcha_shown = False
                            verify_button.click()
                        except BaseException:
                            print('unknown error')

                    self.root_name = temp_root_name
                    root_name = temp_root_name
                    is_created_user_data = self.file_handler.create_aws_user_info(root_password=temp_root_name)
                    self.user_created = is_created_user_data

    def root_confirm(self):
        root_name = generate_root_name()
        time.sleep(2)
        root_field1 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-3"]')
        root_field1.clear()
        self.slow_input(root_field1, sequence=root_name)
        root_field2 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-4"]')
        root_field2.clear()
        self.slow_input(root_field2, sequence=root_name)
        return root_name

    def step_four(self):
        while not self.is_element_present('//*[@id="awsui-radio-button-2"]'):
            time.sleep(1)
        else:
            personal = self.driver.find_element(By.XPATH, '//*[@id="awsui-radio-button-2"]')
            personal.click()
            time.sleep(1)

            full_name_field = self.driver.find_element(By.XPATH, "//div//input[@name='address.fullName']")
            self.slow_input(full_name_field, self.full_name)
            time.sleep(1)

            region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-1"]')
            region.click()
            time.sleep(1)
            country_select = self.driver.find_element(By.XPATH,
                                                      f"//div[contains(@data-value, '{get_country_code(self.phone)}')]")
            country_select.click()
            time.sleep(1)

            phone_field = self.driver.find_element(By.XPATH, '//input[@name="address.phoneNumber"]')
            self.slow_input(phone_field, get_national_number(self.phone))
            time.sleep(1)

            country_or_region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-2"]')
            country_or_region.click()
            found_county = self.driver.find_element(By.XPATH,
                                                    f"//div[contains(@data-value, '{get_country_code(self.phone)}') and contains(@class, 'awsui-select-option-selectable')]")
            found_county.click()
            time.sleep(1)
            address_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-9"]')
            self.slow_input(address_field, self.full_address)
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
            self.update_aws_multiple_fields(root_password=self.root_name,
                                            fields=['first_name', 'last_name', 'phone', 'email',
                                                    'account_name',
                                                    'verify_email_code', 'full_name', 'city', 'state',
                                                    'country',
                                                    'postal_code', 'full_address'])

    def step_five(self):
        time.sleep(3)
        card_number_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-14"]')
        self.slow_input(card_number_field, self.card)

        mouth_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-3"]')
        mouth_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[:2]}']")
        mouth.click()
        time.sleep(2)

        year_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-4"]')
        year_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[3:]}']")
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

        self.file_handler.update_aws_user_info(root_password=self.root_name, field="card",
                                               value=self.card)
        self.file_handler.update_aws_user_info(root_password=self.root_name, field="valid_date", value=self.valid_date)
        self.file_handler.update_aws_user_info(root_password=self.root_name, field="cvv", value=self.cvv)
        self.file_handler.update_aws_user_info(root_password=self.root_name, field="cardholder",
                                               value=self.cardholder_name)

    def step_six(self):
        print('--started step six')
        country_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-5"]')
        country_field.click()
        time.sleep(2)

        region = get_country_code(self.phone)
        mouth = self.driver.find_element(By.XPATH, f"//div[contains(@data-value, '{region}')]")
        mouth.click()
        time.sleep(2)

        national_number_field = self.driver.find_element(By.XPATH, '//*[@id="phoneNumber"]/div/input')
        national_number = get_national_number(self.phone)
        print(f'national number: {national_number}')
        self.slow_input(national_number_field, national_number)
        time.sleep(4)

    def step_seven(self, retry=5, interval=3):
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
            finally:
                warning1 = self.is_shown_warning(warning_xpath="//a[@href='https://aws.amazon.com/support/createCase']",
                                                 name='captcha1')
                warning2 = self.is_shown_warning(
                    warning_xpath="//form[@id='IdentityVerification']//div[contains(text(), 'Security check characters are incorrect. Please try again.')]",
                    name='captcha2')

    def try_solve_captcha(self, xpath, retry=5, interval=3):
        print('trying to solve captcha')
        warning1 = True
        warning2 = True
        while (retry >= 1 and warning1) or (retry >= 1 and warning2):
            try:
                self.captcha_resolve(xpath=xpath)
            except BaseException:
                time.sleep(2)
                retry -= 1
                time.sleep(interval)
            finally:
                warning1 = self.is_shown_warning(warning_xpath="//a[@href='https://aws.amazon.com/support/createCase']",
                                                 name='captcha1')
                warning2 = self.is_shown_warning(
                    warning_xpath="//form[@id='IdentityVerification']//div[contains(text(), 'Security check characters are incorrect. Please try again.')]",
                    name='captcha2')
                if warning1 is False and warning2 is False:
                    print('2 warningns false')
                    return True

    def update_aws_multiple_fields(self, root_password: str, fields: list) -> None:
        for field in fields:
            value = getattr(self, field)  # Get the value of the attribute dynamically
            self.file_handler.update_aws_user_info(root_password=root_password, field=field, value=value)

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
            # time.sleep(random.choice([0.70, 0.91, 0.83, 0.55, 0.41, 0.63, 0.15, 0.21, 0.33]))
            time.sleep(0.03)

    def is_shown_warning(self, warning_xpath: str = '', name: str = None) -> bool:
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

    def is_element_present(self, locator: str, by_type: str = 'xpath', name: str = '') -> bool:
        try:
            element = self.driver.find_element(by_type, locator)
            if element is not None:
                print('Element found')
                return True
            else:
                return False
        except NoSuchElementException:
            print(f"Element {locator} with type {by_type} not found {name}")
            return False
        except Exception as e:
            print(f"Unknown Error {e} {name}")
            return False

    def wait_for_element(self, locator, by_type='xpath', timeout=30, poll_frequency=0.5):
        element = None
        try:
            self.driver.implicitly_wait(0)
            print(f"Waiting for maximum ---{str(timeout)} ---- seconds for element")
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
        self.open_page()  # TODO and made all tests
        self.step_one()
        self.step_two()
        self.step_three()
        self.step_four()
        self.step_five()
        self.step_six()
        self.step_seven()
        time.sleep(32)
