import asyncio
import time

from async_simhandler import AsyncOnlineSimHandler
from config import configs
from imap_handler import ImapHandler
from logs.aws_logger import awslogger
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from utils.element_handler import ElementHandler
from utils.file_handler import FileHandler
from utils.phone_identifier import get_country_code, get_national_number
from utils.randomizer import generate_first_last_name, generate_root_name
from utils.randomizer import generate_random_addresses as addresses
from utils.temp_mail import check_last_message, generate_mail


class BaseRegistrator:
    def __init__(self):
        """
        Base class for registration.

        Initializes the Chrome WebDriver.
        """
        self.USERNAME = configs.private_configs.USERNAME
        self.PASSWORD = configs.private_configs.PASSWORD
        self.ENDPOINT = configs.private_configs.ENDPOINT
        self.driver = self.create_browser()

    def create_driver(self):
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument("--lang=en-US")
        options.add_argument("--user-agent=Mozilla/5.4235.Safari/23.Windows10.1")
        prefs = {}
        prefs["profile.default_content_settings.popups"] = 0
        prefs["profile.default_content_setting_values.cookies"] = 1
        prefs["profile.cookie_controls_mode"] = 0

        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        wire_options = {
            'proxy': {
                'http': f'https://customer-awsworker-sessid-0198906550-sesstime-10:{self.PASSWORD}@{self.ENDPOINT}',
                'https': f'https://customer-awsworker-sessid-0198906550-sesstime-10:{self.PASSWORD}@{self.ENDPOINT}',
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
        return webdriver.Chrome(options=options, seleniumwire_options=wire_options)

    def create_browser(self):
        self.driver = self.create_driver()
        self.driver.maximize_window()
        return self.driver


class AwsRegistrator(BaseRegistrator):
    def __init__(self, email: str = None, password: str = None):
        """
        AWS registration class.

        Args:
            email (str, optional): The email address for registration.
            password (str, optional): The password for registration.
        """
        self.email = email
        self.card = configs.private_configs.CARD_NUMBER
        self.file_handler = FileHandler()
        self.file_handler.validate_card_and_email(email=self.email, card=self.card)
        super().__init__()
        self.element_handler = ElementHandler(driver=self.driver)
        self.password = password
        self.valid_date = self.get_valid_date()
        self.cvv = configs.private_configs.CVV
        self.account_name = email[0:-4].capitalize()
        self.user_created = False
        self.sim_handler = AsyncOnlineSimHandler(api_token=configs.private_configs.SIM_API_TOKEN)
        self.root_name = None
        self.verify_email_code = None
        self.phone = None
        self.first_name, self.last_name = generate_first_last_name()
        self.full_name = f"{self.first_name} {self.last_name}"
        self.cardholder = configs.private_configs.CARDHOLDER
        self.address, self.city, self.state, self.postal_code, self.country, self.full_address = addresses().values()
        self.url = configs.aws_configs.URL
        if password:
            self.imap_instance = ImapHandler(self.email, self.password)

    def get_valid_date(self, expire_date: str = configs.private_configs.EXPIRE_DATE) -> str:
        """
        Returns a valid date based on the provided `expire_date`.

        Args:
            expire_date (str, optional): The input expiration date.
            Defaults to the value from `configs.private_configs.EXPIRE_DATE`.

        Returns:
            str: A valid bank expire date in the format 'MM/YYYY'.
        """
        if len(expire_date[3:]) == 2:
            valid_date = expire_date[:3] + '20' + expire_date[3:]
            return valid_date
        else:
            return configs.private_configs.EXPIRE_DATE

    def open_page(self) -> None:
        """
        Opens the registration page.

        Returns:
            None
        """
        self.driver.maximize_window()
        self.driver.get(self.url)

    def step_one(self, email: str = None, retry: int = 5, interval: int = 5) -> None:
        """
        Performs step one of the registration process.

        Args:
            email (str, optional): The email address for registration.
            retry (int, optional): Number of retry attempts (default is 5).
            interval (int, optional): Interval between retries (default is 5 seconds).

        Returns:
            None
        """
        warning_email = True
        while retry >= 1 and warning_email:
            try:
                self.email_confirm()
            except NoSuchElementException:
                retry -= 1
                time.sleep(interval)
                awslogger.log_error(f"Trying confirm email {5 - retry}'d time")
            finally:
                warning_email = self.element_handler.is_shown_warning(warning_xpath='//*[@id="awsui-input-0"]',
                                                                      name='email warning')

    def email_confirm(self, email: str = None) -> str:
        """
        Confirm the email address during registration.

        Args:
            email (str, optional): The email address to confirm (default is None).

        Returns:
            str: The confirmed email address.
        """
        root_email_field = self.element_handler.wait_for_element(locator="//div//input[@name='emailAddress']",
                                                                 timeout=5, name='root email field')
        root_email_field.clear()
        if email is None:
            self.element_handler.slow_input(root_email_field, self.email)
        else:
            email = generate_mail()
            self.email = email
        acc_name_field = self.element_handler.wait_for_element(locator="//div//input[@name='fullName']", timeout=6,
                                                               name='account field', )
        acc_name_field.clear()
        self.account_name = self.email[0:-4].capitalize()
        self.element_handler.slow_input(acc_name_field, self.account_name)
        verify_email = self.driver.find_element(By.XPATH,
                                                '//*[@id="EmailValidationSendOTP"]/fieldset/awsui-button[1]/button')
        verify_email.click()
        time.sleep(2)
        return email

    def step_two(self) -> None:
        """
        Perform step two of the registration process with checking email and get verify code to fill it.

        Returns:
            None
        """
        confirm_mail = self.element_handler.wait_for_element("//awsui-input[@id='otp']/div/input[@name='otp']",
                                                             timeout=5, name='cofirm mail field', )
        confirm_mail.clear()
        if not self.password:
            verify_code = check_last_message(self.email)
        else:
            verify_code = self.imap_instance.mailbox_confirm_message()
        if verify_code:
            verify_button = self.driver.find_element(By.XPATH,
                                                     '//*[@id="EmailValidationVerifyOTP"]/fieldset/awsui-button[1]/button')
            self.element_handler.slow_input(confirm_mail, sequence=verify_code)
            self.verify_email_code = verify_code
            verify_button.click()
            time.sleep(2)
        while not verify_code:
            # not_you_button = self.driver.find_element(By.XPATH,
            #                                           "//*[@id='EmailValidationVerifyOTP']/fieldset/p/span[contains(text(), 'not you')]")
            not_you_button = self.element_handler.wait_for_element(
                locator="//*[@id='EmailValidationVerifyOTP']/fieldset/p/span[contains(text(), 'not you')]",
                name='not you button')
            not_you_button.click()
            self.step_one()

    def step_three(self, retry: int = 15, interval: int = 4) -> None:
        """
        Perform step three of the registration process.

        Args:
            retry (int, optional): Number of retry attempts (default is 15).
            interval (int, optional): Interval between retries (default is 4 seconds).

        Returns:
            None
        """
        root_name = False
        warning_shown = True
        verify_button = self.element_handler.wait_for_element(
            locator="//*[@id='CredentialCollection']/fieldset/awsui-button[1]/button[span[text()='Continue (step 1 of 5)']]",
            name='verify button root')
        while not root_name and warning_shown:
            try:
                temp_root_name = self.root_confirm()
            except BaseException:
                time.sleep(interval)
                retry -= 1
            finally:
                warning_shown = self.element_handler.is_element_present(
                    locator="//a[@href='https://support.aws.amazon.com/#/contacts/aws-account-support']",
                    name='warning on root step')
                if not warning_shown and temp_root_name:
                    self.element_handler.try_solve_captcha(
                        xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
                    verify_button.click()
                    time.sleep(2)
                    self.root_name = temp_root_name
                    root_name = temp_root_name
                    is_created_user_data = self.file_handler.create_aws_user_info(root_password=temp_root_name)
                    self.user_created = is_created_user_data
                else:
                    verify_button.click()

    def root_confirm(self) -> str:
        """
        Confirm the root name during registration.

        Returns:
            str: The confirmed root name.
        """
        root_name = generate_root_name()
        root_field1 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-3"]')
        root_field1.clear()
        self.element_handler.slow_input(root_field1, sequence=root_name)
        root_field2 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-4"]')
        root_field2.clear()
        self.element_handler.slow_input(root_field2, sequence=root_name)
        return root_name

    def step_four(self) -> None:
        """
        Perform step four of the registration process with filling and confirming personal address information.

        Returns:
            None
        """
        while not self.element_handler.is_element_present('//*[@id="awsui-radio-button-2"]'):
            time.sleep(1)
        else:
            personal = self.driver.find_element(By.XPATH, '//*[@id="awsui-radio-button-2"]')
            personal.click()
            time.sleep(1)
            full_name_field = self.driver.find_element(By.XPATH, "//div//input[@name='address.fullName']")
            self.element_handler.slow_input(full_name_field, self.full_name)
            self.phone = asyncio.run(self.sim_handler.order_phone_number())
            region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-1"]')
            region.click()
            time.sleep(1)
            country_select = self.driver.find_element(By.XPATH,
                                                      f"//div[contains(@data-value, '{get_country_code(self.phone)}')]")
            country_select.click()
            phone_field = self.driver.find_element(By.XPATH, '//input[@name="address.phoneNumber"]')
            self.element_handler.slow_input(phone_field, get_national_number(self.phone))

            country_or_region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-2"]')
            country_or_region.click()
            found_county = self.driver.find_element(By.XPATH,
                                                    f"//div[contains(@data-value, '{get_country_code(self.phone)}') and contains(@class, 'awsui-select-option-selectable')]")
            found_county.click()
            address_field = self.driver.find_element(By.XPATH, '//input[@name="address.addressLine1"]')
            self.element_handler.slow_input(address_field, self.full_address)
            city = self.driver.find_element(By.XPATH, '//input[@name="address.city"]')
            self.element_handler.slow_input(city, self.city)
            state_region_field = self.driver.find_element(By.XPATH, '//input[@name="address.state"]')
            self.element_handler.slow_input(state_region_field, self.state)
            postal_code = self.driver.find_element(By.XPATH, '//input[@name="address.postalCode"]')
            self.element_handler.slow_input(postal_code, self.postal_code)
            agree_checkbox = self.driver.find_element(By.XPATH, '//input[@name="agreement"]')
            agree_checkbox.click()
            continue_button = self.driver.find_element(By.XPATH,
                                                       '//*[@id="ContactInformation"]/fieldset/awsui-button/button')
            continue_button.click()
            time.sleep(2)
            self.update_aws_multiple_fields(root_password=self.root_name,
                                            fields=['first_name', 'last_name', 'phone', 'email',
                                                    'account_name',
                                                    'verify_email_code', 'full_name', 'city',
                                                    'country',
                                                    'postal_code', 'full_address', ])

    def step_five(self) -> None:
        """
        Perform step five of the registration process with filling card info and confirming it.

        Returns:
            None
        """
        card_number_field = self.element_handler.wait_for_element(locator='//input[@name="cardNumber"]',
                                                                  name='card_field')

        self.element_handler.slow_input(card_number_field, self.card)

        mouth_field = self.driver.find_element(By.XPATH, '//div[@placeholder="Month"]')
        mouth_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[:2]}']")
        mouth.click()

        year_field = self.driver.find_element(By.XPATH, '//div[@placeholder="Year"]')
        year_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[3:]}']")
        mouth.click()

        cvv_field = self.driver.find_element(By.XPATH, '//input[@placeholder="CVV/CVC"]')
        self.element_handler.slow_input(cvv_field, self.cvv)

        cardholder_field = self.driver.find_element(By.XPATH, '//input[@name="accountHolderName"]')
        self.element_handler.slow_input(cardholder_field, self.cardholder)

        verify_step = self.driver.find_element(By.XPATH,
                                               '//*[@id="PaymentInformation"]/fieldset/awsui-button/button')
        verify_step.click()
        time.sleep(2)

        self.update_aws_multiple_fields(root_password=self.root_name,
                                        fields=['card', 'valid_date', 'cvv', 'cardholder'])

    def step_six(self) -> None:
        """
        Perform step six of the registration process with phone and region info.

        Returns:
            None
        """
        country_field = self.element_handler.wait_for_element(locator='//*[@id="awsui-select-5"]',
                                                              name='country_field')

        country_field.click()
        region = get_country_code(self.phone)
        month = self.element_handler.wait_for_element(locator=f"//div[contains(@data-value, '{region}')]",
                                                      timeout=10,
                                                      name='month_field')
        month.click()
        national_number_field = self.element_handler.wait_for_element(locator='//*[@id="phoneNumber"]/div/input',
                                                                      timeout=10, name='national_number_field')
        national_number = get_national_number(self.phone)
        awslogger.log_info(f'national number: {national_number}')
        self.element_handler.slow_input(national_number_field, national_number)

    def step_seven(self) -> None:
        """
        Perform step seven of the registration process with solving captcha.

        Returns:
            None
        """
        self.element_handler.try_solve_captcha(
            xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
        verify = self.driver.find_element(By.XPATH, "//button[span[text()='Send SMS (step 4 of 5)']]")
        verify.click()
        time.sleep(2)

    def step_eight(self) -> None:
        """
        Perform step eight of the registration process with receiving sms message, input it and confirm.

        Returns:
            None
        """
        sim_info = asyncio.run(self.sim_handler.wait_order_info())
        sms_code = sim_info['sms']
        sms_input_field = self.element_handler.wait_for_element(locator='//div//input[@name="smsPin"]',
                                                                name='sms field',
                                                                timeout=10)
        sms_input_field.clear()
        self.element_handler.slow_input(sms_input_field, sms_code)

        verify_sms_button = self.driver.find_element(By.XPATH, '//button[contains(span, "Continue (step 4 of 5)")]')
        verify_sms_button.click()
        self.file_handler.update_aws_user_info(root_password=self.root_name, field='phone', value=self.phone)
        finish_button = self.element_handler.wait_for_element(
            locator='//*[@id="SupportPlan"]/fieldset/div[2]/awsui-button/button', name='finish button')
        finish_button.click()
        time.sleep(2)

    def update_aws_multiple_fields(self, root_password: str, fields: list) -> None:
        """
            Update AWS user multiple fields.

            Args:
                root_password (str): The root password.
                fields (list): List of fields to update.

            Returns:
                None
            """
        for field in fields:
            value = getattr(self, field)
            self.file_handler.update_aws_user_info(root_password=root_password, field=field, value=value)

    def register(self) -> None:
        """
        Registers an AWS account by completing the required steps.

        Returns:
            None
        """
        self.open_page()
        self.step_one()
        self.step_two()
        self.step_three()
        self.step_four()
        self.step_five()
        self.step_six()
        self.step_seven()
        self.step_eight()
        self.driver.quit()
