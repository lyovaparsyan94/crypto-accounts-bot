import time
import json
import undetected_chromedriver as uc
from helpers.temp_mail import check_last_message
from selenium import webdriver
from helpers.randomizer import generate_root_name
from imap_handler import ImapHandler
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AwsRegistrator:
    def __init__(self, email=None, password=None):
        self.options = uc.ChromeOptions()
        self.options.add_argument("--proxy-server=171.243.3.55:4006")
        self.options.add_argument(r'--user-data-dir=C:\Users\parsy\AppData\Local\Google\Chrome\User Data\Profile')
        # self.driver = webdriver.Chrome()
        self.driver = uc.Chrome(options=self.options)
        self.email = email
        self.password = password
        self.account_name = email[0:-4].capitalize()
        self.tell_number = "2013514000"
        self.first_name = "Pau"
        self.last_name = "Storer"
        self.full_name = f"{self.first_name} {self.last_name}"
        self.bank_number = "4278627431140307"
        self.valid_date = "08/25"
        self.cvv = "678"
        self.city = 'Richmond'
        self.state = 'VA'
        self.postal_code = '23235'
        self.address = f'1913 Belleau Dr, {self.city}, {self.state} {self.postal_code}, USA'
        self.url = "https://portal.aws.amazon.com/billing/signup#/identityverification"
        if password:
            self.imap_instance = ImapHandler(self.email, self.password)

    def open_page(self):
        self.driver.maximize_window()
        self.driver.get('https://browserleaks.com/ip')
        time.sleep(9)
        self.driver.get(self.url)

    def step_one(self):
        root_email = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-0"]')
        root_email.clear()
        self.slow_input(root_email, self.email)
        time.sleep(1)

        acc_name = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-1"]')
        self.slow_input(acc_name, self.account_name)
        verify_email = self.driver.find_element(By.XPATH,
                                                '//*[@id="EmailValidationSendOTP"]/fieldset/awsui-button[1]/button')
        verify_email.click()
        print('Finish step one')

    def step_two(self):
        time.sleep(3)
        confirm_mail = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-2"]')
        confirm_mail.clear()
        if self.password:
            verify_code = self.imap_instance.mailbox_confirm_message()
        else:
            verify_code = check_last_message(self.email)
        self.slow_input(confirm_mail, sequence=verify_code)
        verify_button = self.driver.find_element(By.XPATH,
                                                 '//*[@id="EmailValidationVerifyOTP"]/fieldset/awsui-button[1]/button')
        time.sleep(2)
        verify_button.click()
        print('finished step two')

    def step_three(self):
        time.sleep(3)
        root = self.account_name + '!!1@1@#'
        root_field1 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-3"]')
        root_field1.clear()
        self.slow_input(root_field1, sequence=root)
        root_field2 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-4"]')
        root_field2.clear()
        time.sleep(4)
        self.slow_input(root_field2, sequence=root)
        print(f'filled root {root}')

        verify = self.driver.find_element(By.XPATH, '//*[@id="CredentialCollection"]/fieldset/awsui-button[1]/button')
        verify.click()
        time.sleep(3)

        # some_error = self.driver.find_element(By.XPATH, '//*[@id="CredentialCollection"]/fieldset/awsui-alert[1]/div/div[2]/div/div/span/text()[1]')

    def step_four(self):
        personal = self.driver.find_element(By.XPATH, '//*[@id="awsui-radio-button-2"]')
        personal.click()
        time.sleep(1)

        full_name_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-5"]')
        self.slow_input(full_name_field, self.full_name)
        time.sleep(1)

        phone_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-7"]')
        self.slow_input(phone_field, self.tell_number)
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
        time.sleep(3)
        card_number_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-14"]')
        self.slow_input(card_number_field, self.bank_number)

        # mouth = self.driver.find_element(By.ID, '//*[@id="expirationMonth"]')
        # sel = Select(mouth)
        # sel.select_by_value('March')
        mouth_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-3"]')
        mouth_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='{self.valid_date[:2]}']")
        mouth.click()

        year_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-select-4"]')
        year_field.click()
        mouth = self.driver.find_element(By.XPATH, f"//div[@data-value='20{self.valid_date[3:]}']")
        mouth.click()

        cvv_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-15"]')
        self.slow_input(cvv_field, self.cvv)

        cardholder_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-16"]')
        self.slow_input(cardholder_field, self.full_name)

        verify_step = self.driver.find_element(By.XPATH, '//*[@id="PaymentInformation"]/fieldset/awsui-button/button')
        verify_step.click()
        time.sleep(5)

    @staticmethod
    def slow_input(field_to_fill, sequence):
        for symbol in sequence:
            field_to_fill.send_keys(symbol)
            # time.sleep(random.choice([0.70, 0.91, 0.83, 0.55, 0.41, 0.63, 0.15, 0.21, 0.33]))
            # time.sleep(0.05)

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

    def register(self):
        self.open_page()
        time.sleep(5)
        self.step_one()
        time.sleep(5)
        self.step_two()
        time.sleep(5)
        self.step_three()
        time.sleep(5)
        self.step_four()
        time.sleep(5)
        self.step_five()
        time.sleep(32)
