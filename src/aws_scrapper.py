import time
import json
from itertools import chain
from selenium import webdriver
from imap_handler import ImapHandler
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AwsRegistrator:
    def __init__(self, email, password):
        self.driver = webdriver.Chrome()
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
        self.imap_instance = ImapHandler(self.email, self.password)
        self.url = "https://portal.aws.amazon.com/billing/signup#/identityverification"

    def open_page(self):
        self.driver.maximize_window()
        time.sleep(2)
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
        confirm_mail = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-2"]')
        confirm_mail.clear()
        verify_code = self.imap_instance.mailbox_confirm_message()
        # verify_code = '131478'
        if verify_code:
            self.slow_input(confirm_mail, sequence=verify_code)
            verify_button = self.driver.find_element(By.XPATH,
                                                     '//*[@id="EmailValidationVerifyOTP"]/fieldset/awsui-button[1]/button')
            time.sleep(2)
            verify_button.click()
            return verify_code
        else:
            print('Not Found verification code')

    def step_three(self, verify_code):
        root = f"{self.account_name}+{verify_code}"
        root_field1 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-3"]')
        root_field1.clear()
        self.slow_input(root_field1, sequence=root)
        root_field2 = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-4"]')
        root_field2.clear()
        self.slow_input(root_field2, sequence=root)
        print('Passed root code')
        verify = self.driver.find_element(By.XPATH, '//*[@id="CredentialCollection"]/fieldset/awsui-button[1]/button')
        verify.click()
        time.sleep(7)

    def step_four(self):
        personal = self.driver.find_element(By.XPATH, '//*[@id="awsui-radio-button-2"]')
        personal.click()
        time.sleep(1)

        full_name_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-5"]')
        self.slow_input(full_name_field, self.full_name)
        time.sleep(1)

        phone_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-10"]')
        self.slow_input(phone_field, self.tell_number)
        time.sleep(1)

        address_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-12"]')
        self.slow_input(address_field, self.address)
        time.sleep(1)

        city = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-14"]')
        self.slow_input(city, self.city)
        time.sleep(1)

        state_region_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-15"]')
        self.slow_input(state_region_field, self.state)
        time.sleep(1)

        postal_code = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-16"]')
        self.slow_input(postal_code, self.postal_code)
        time.sleep(1)

        agree_checkbox = self.driver.find_element(By.XPATH, '//*[@id="awsui-checkbox-0"]')
        agree_checkbox.click()

        continue_button = self.driver.find_element(By.XPATH, '//*[@id="ContactInformation"]/fieldset/awsui-button/button')
        continue_button.click()
        time.sleep(10)

    def step_five(self):
        card_number_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-17"]')
        self.slow_input(card_number_field, self.bank_number)

        mouth = self.driver.find_element(By.ID, '//*[@id="expirationMonth"]')
        sel = Select(mouth)
        sel.select_by_value('March')

        year = self.driver.find_element(By.XPATH, '//*[@id="expirationYear"]')
        sel = Select(year)
        sel.select_by_value('2026')

        cvv_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-18"]')
        self.slow_input(cvv_field, self.cvv)

        cardholder_field = self.driver.find_element(By.XPATH, '//*[@id="awsui-input-19"]')
        self.slow_input(cardholder_field, self.full_name)

        verify_step = self.driver.find_element(By.XPATH, '//*[@id="PaymentInformation"]/fieldset/awsui-button/button')
        verify_step.click()
        time.sleep(5)


    @staticmethod
    def slow_input(field_to_fill, sequence):
        for symbol in sequence:
            field_to_fill.send_keys(symbol)
            # time.sleep(random.choice([0.70, 0.91, 0.83, 0.55, 0.41, 0.63, 0.15, 0.21, 0.33]))
            time.sleep(0.05)

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
        code = self.step_two()
        time.sleep(5)
        self.step_three(code)
        time.sleep(5)
        self.step_four()
        time.sleep(5)
        self.step_five()
        time.sleep(32)


