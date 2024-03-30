import time

import undetected_chromedriver as uc
from async_simhandler import AsyncOnlimeSimHandler
from configs.constants import CARD_NUMBER, CARDHOLDER, CVV, EXPIRE_DATE, URL
from helpers.element_handler import ElementHandler
from helpers.file_handler import FileHandler
from helpers.phone_identifier import get_country_code, get_national_number
from helpers.randomizer import generate_first_last_name, generate_root_name
from helpers.randomizer import generate_random_addresses as addresses
from helpers.temp_mail import check_last_message, generate_mail
from imap_handler import ImapHandler
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


class AwsRegistrator:
    def __init__(self, email=None, password=None):
        self.options = uc.ChromeOptions()
        # self.options = Options()
        self.file_handler = FileHandler()
        self.user_created = False
        # self.options.add_argument("--proxy-server=159.203.61.169:3128")
        # self.options.add_argument(rf'--user-data-dir={USER_DATA_DIR}')
        self.options.add_argument(r'--user-data-dir=C:\Users\parsy\AppData\Local\Google\Chrome\User Data\Profile')
        self.driver = webdriver.Chrome()
        self.driver = uc.Chrome(options=self.options)
        # self.driver = webdriver.Chrome(options=self.options)
        self.element_handler = ElementHandler(driver=self.driver)
        self.email = email
        self.root_name = None
        self.password = password
        self.verify_email_code = None
        self.account_name = email[0:-4].capitalize()
        # self.phone = "+37477970340"
        # self.sim_handler = OnlineSimHandler()
        self.sim_handler = AsyncOnlimeSimHandler()
        self.phone = None
        self.first_name, self.last_name = generate_first_last_name()
        self.full_name = f"{self.first_name} {self.last_name}"
        # self.cardholder = generate_cardholder_name()
        self.cardholder = CARDHOLDER
        # self.card, self.cvv, self.valid_date = card_data()['card_number'], card_data()['cvv'], card_data()['expiry_date']
        self.card, self.cvv, self.valid_date = CARD_NUMBER, CVV, EXPIRE_DATE
        self.address, self.city, self.state, self.postal_code, self.country, self.full_address = addresses().values()
        self.url = URL
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
            except NoSuchElementException:
                retry -= 1
                time.sleep(interval)
                retry -= 5
                print(f"Confirming email {5 - retry} time")
            finally:
                warning_email = self.element_handler.is_shown_warning(warning_xpath='//*[@id="awsui-input-0"]',
                                                                      name='email warning')

    def email_confirm(self, email=None):
        root_email_field = self.element_handler.wait_for_element(locator="//div//input[@name='emailAddress']",
                                                                 timeout=10, name='root email field')
        while not root_email_field:
            time.sleep(1)
        else:
            root_email_field.clear()
        if email is None:
            self.element_handler.slow_input(root_email_field, self.email)
        else:
            email = generate_mail()
            self.email = email
        time.sleep(1)
        # acc_name = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-1"]')
        acc_name_field = self.element_handler.wait_for_element(locator="//div//input[@name='fullName']", timeout=6,
                                                               name='account field')
        while not self.element_handler.is_element_present(locator="//div//input[@name='fullName']"):
            time.sleep(1)
        else:
            acc_name_field.clear()
        self.account_name = self.email[0:-4].capitalize()
        self.element_handler.slow_input(acc_name_field, self.account_name)
        verify_email = self.driver.find_element(By.XPATH,
                                                '//*[@id="EmailValidationSendOTP"]/fieldset/awsui-button[1]/button')
        verify_email.click()
        time.sleep(3)
        return email

    def step_two(self):
        confirm_mail = self.element_handler.wait_for_element("//awsui-input[@id='otp']/div/input[@name='otp']",
                                                             timeout=5)
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
            # need_resend = self.driver.find_element(By.XPATH,
            #                                        '//div[@class="awsui-alert-body"]//div[@class="awsui-alert-message"]//div[@awsui-alert-region="content"]')
            # if need_resend.is_displayed():
            #     resend_button = self.driver.find_element(By.XPATH,
            #                                              '//*[@id="EmailValidationVerifyOTP"]/fieldset/awsui-button[2]/button')
            #     verify_code = None
            #     resend_button.click()
            #     self.step_two()
            # self.another_form(imap_data)
        while not verify_code:
            not_you_button = self.driver.find_element(By.XPATH,
                                                      "//*[@id='EmailValidationVerifyOTP']/fieldset/p/span[contains(text(), 'not you')]")
            not_you_button.click()
            self.step_one()

    def step_three(self, retry=15, interval=4):
        root_name = False
        warning_shown = True
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
                # time.sleep(2)
                warning_shown = self.element_handler.is_element_present(
                    locator="//a[@href='https://support.aws.amazon.com/#/contacts/aws-account-support']")
                if not warning_shown and temp_root_name:
                    captcha_shown = self.element_handler.is_shown_warning(
                        warning_xpath='//div[contains(@class, "Captcha_mainDisplay")]', name='captcha')
                    while captcha_shown:
                        try:
                            self.element_handler.try_solve_captcha(
                                xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
                            verify_button.click()
                            time.sleep(2)
                            captcha_shown = self.element_handler.wait_for_element(
                                locator='//div[contains(@class, "Captcha_mainDisplay")]', timeout=3, name='captcha')
                        except BaseException:
                            print('unknown error')
                    self.root_name = temp_root_name
                    root_name = temp_root_name
                    is_created_user_data = self.file_handler.create_aws_user_info(root_password=temp_root_name)
                    self.user_created = is_created_user_data

    def root_confirm(self):
        root_name = generate_root_name()
        root_field1 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-3"]')
        root_field1.clear()
        self.element_handler.slow_input(root_field1, sequence=root_name)
        root_field2 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-4"]')
        root_field2.clear()
        self.element_handler.slow_input(root_field2, sequence=root_name)
        return root_name

    def step_four(self):
        while not self.element_handler.is_element_present('//*[@id="awsui-radio-button-2"]'):
            time.sleep(1)
        else:
            personal = self.driver.find_element(By.XPATH, '//*[@id="awsui-radio-button-2"]')
            personal.click()
            time.sleep(1)

            full_name_field = self.driver.find_element(By.XPATH, "//div//input[@name='address.fullName']")
            self.element_handler.slow_input(full_name_field, self.full_name)

            self.sim_handler.can_receive = True
            self.phone = self.sim_handler.order_number()
            region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-1"]')
            region.click()
            time.sleep(1)
            country_select = self.driver.find_element(By.XPATH,
                                                      f"//div[contains(@data-value, '{get_country_code(self.phone)}')]")
            country_select.click()
            time.sleep(1)

            phone_field = self.driver.find_element(By.XPATH, '//input[@name="address.phoneNumber"]')
            self.element_handler.slow_input(phone_field, get_national_number(self.phone))
            time.sleep(1)

            country_or_region = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-2"]')
            country_or_region.click()
            found_county = self.driver.find_element(By.XPATH,
                                                    f"//div[contains(@data-value, '{get_country_code(self.phone)}') and contains(@class, 'awsui-select-option-selectable')]")
            found_county.click()
            address_field = self.driver.find_element(By.XPATH, '//input[@name="address.addressLine1"]')
            self.element_handler.slow_input(address_field, self.full_address)
            time.sleep(1)

            city = self.driver.find_element(By.XPATH, '//input[@name="address.city"]')
            self.element_handler.slow_input(city, self.city)
            time.sleep(1)

            state_region_field = self.driver.find_element(By.XPATH, '//input[@name="address.state"]')
            self.element_handler.slow_input(state_region_field, self.state)
            time.sleep(1)

            postal_code = self.driver.find_element(By.XPATH, '//input[@name="address.postalCode"]')
            self.element_handler.slow_input(postal_code, self.postal_code)
            time.sleep(1)

            agree_checkbox = self.driver.find_element(By.XPATH, '//input[@name="agreement"]')
            agree_checkbox.click()

            continue_button = self.driver.find_element(By.XPATH,
                                                       '//*[@id="ContactInformation"]/fieldset/awsui-button/button')
            continue_button.click()
            time.sleep(2)
            self.update_aws_multiple_fields(root_password=self.root_name,
                                            fields=['first_name', 'last_name', 'phone', 'email',
                                                    'account_name',
                                                    'verify_email_code', 'full_name', 'city', 'state',
                                                    'country',
                                                    'postal_code', 'full_address'])

    def step_five(self):
        card_number_field = self.element_handler.wait_for_element(locator='//input[@name="cardNumber"]',
                                                                  name='card_field', timeout=3)
        while not card_number_field:
            time.sleep(0.5)
        else:
            self.element_handler.slow_input(card_number_field, self.card)

            mouth_field = self.driver.find_element(By.XPATH, '//div[@placeholder="Month"]')
            mouth_field.click()
            mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[:2]}']")
            mouth.click()
            time.sleep(2)

            year_field = self.driver.find_element(By.XPATH, '//div[@placeholder="Year"]')
            year_field.click()
            mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[3:]}']")
            mouth.click()
            time.sleep(1)

            cvv_field = self.driver.find_element(By.XPATH, '//input[@placeholder="CVV/CVC"]')
            self.element_handler.slow_input(cvv_field, self.cvv)
            time.sleep(1)

            cardholder_field = self.driver.find_element(By.XPATH, '//input[@name="accountHolderName"]')
            self.element_handler.slow_input(cardholder_field, self.cardholder)

            verify_step = self.driver.find_element(By.XPATH, '//*[@id="PaymentInformation"]/fieldset/awsui-button/button')
            verify_step.click()

            self.update_aws_multiple_fields(root_password=self.root_name,
                                            fields=['card', 'valid_date', 'cvv', 'cardholder'])

    def step_six(self):
        country_field = self.element_handler.wait_for_element(locator='//*[@id="awsui-select-5"]', timeout=10,
                                                              name='country_field')
        while not country_field:
            time.sleep(0.5)
        else:
            country_field.click()
            region = get_country_code(self.phone)
            month = self.element_handler.wait_for_element(locator=f"//div[contains(@data-value, '{region}')]", timeout=10,
                                                          name='month_field')
            month.click()
            national_number_field = self.element_handler.wait_for_element(locator='//*[@id="phoneNumber"]/div/input',
                                                                          timeout=10, name='national_number_field')
            national_number = get_national_number(self.phone)
            print(f'national number: {national_number}')
            self.element_handler.slow_input(national_number_field, national_number)

    def step_seven(self):
        self.element_handler.try_solve_captcha(
            xpath="//div[contains(@class, 'Captcha_mainDisplay')]//img[@alt='captcha']")
        verify = self.driver.find_element(By.XPATH, "//button[span[text()='Send SMS (step 4 of 5)']]")
        verify.click()

    def step_eight(self):
        sms_code = self.sim_handler.wait_order_info()['sms']
        sms_input_field = self.element_handler.wait_for_element(locator='//div//input[@name="smsPin"]',
                                                                name='sms field',
                                                                timeout=10)
        while not sms_input_field:
            time.sleep(0.5)
        else:
            sms_input_field.clear()
            self.element_handler.slow_input(sms_input_field, sms_code)

            verify_sms_button = self.driver.find_element(By.XPATH, '//button[contains(span, "Continue (step 4 of 5)")]')
            verify_sms_button.click()
            self.file_handler.update_aws_user_info(root_password=self.root_name, field='phone', value=self.phone)
            time.sleep(5)
            finish_button = self.driver.find_element(By.XPATH, '//*[@id="SupportPlan"]/fieldset/div[2]/awsui-button/button')
            time.sleep(2)
            finish_button.click()

    def update_aws_multiple_fields(self, root_password: str, fields: list) -> None:
        for field in fields:
            value = getattr(self, field)  # Get the value of the attribute dynamically
            self.file_handler.update_aws_user_info(root_password=root_password, field=field, value=value)

    def another_form(self, imap_data):
        self.driver.get(imap_data)
        time.sleep(3)
        fill_mail_field = self.driver.find_element(By.ID, 'resolving_input')
        self.element_handler.slow_input(fill_mail_field, self.email)
        next_button = self.driver.find_element(By.ID, 'next_button')
        next_button.click()
        time.sleep(3)
        pass_field = self.driver.find_element(By.ID, 'password')
        self.element_handler.slow_input(pass_field, self.password)
        time.sleep(1)
        sign_in = self.driver.find_element(By.ID, 'signin_button')
        sign_in.click()
        time.sleep(5)

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
        self.step_eight()
        time.sleep(32)
