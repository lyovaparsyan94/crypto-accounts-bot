import re
from pprint import pprint
from time import sleep

import requests


class OnlineSimHandler:

    def __init__(self, api_key=None, country=44):
        self.api_key = api_key
        self.phone_national = '7466701102'
        self.country = country
        self.phone = f"+{self.country}{self.phone_national}"

    def get_online_sim_data(self):
        # Extract parameters from the options object
        fullUrl = f"https://onlinesim.io/api/getFreeList?country={self.country}&number={self.phone_national}&lang=en"
        method = "GET"
        mimeType = "application/x-www-form-urlencoded"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
        }
        postData = {
        }
        cookies = {

        }
        # Set up the request
        req = requests.Request(method, fullUrl, headers=headers, cookies=cookies)
        # Add data to the request
        if postData:
            req.data = postData
        # Construct the prepared request
        prepared_req = req.prepare()
        # Send the request and get the response
        session = requests.Session()
        response = session.send(prepared_req)
        # Handle the response
        print(f"{response.status_code} {response.reason}")
        messages = response.json()['messages']
        messages_text = messages['data']
        if response.status_code == 200:
            pprint(messages_text)
            return messages_text
        else:
            return None
        # if response.status_code >= 400:
        #     print("Error:", response.status_code, response.reason)

    def get_aws_code(self, retry: int = 15, interval: int = 10) -> bool | str:
        sms_code = False
        while not sms_code and retry >= 1:
            try:
                messages = self.get_online_sim_data()
                if messages:
                    for message in messages:
                        sender = message['in_number']
                        code = message['code']
                        text_of_message = message['text']
                        # if sender.lower() in 'Amazon Web Services (AWS) aws 64018'.lower():
                        if 'Amazon OTP' in text_of_message:
                            print('sender', sender, '\ncode', code, '\nmessage', message['text'], message['date'])
                            if len(code) > 1:
                                sms_code = code
                                return sms_code
                        else:
                            verification_string = message['text']
                            if 'is your Amazon OTP' in verification_string:
                                match = re.search(r"\d{4}", verification_string)
                                if match:
                                    verification_code = match.group()
                                    print(f"Verification code: {verification_code}, sender: {sender}")
                                    sms_code = verification_code
                                    return sms_code
            except BaseException:
                retry -= 1
                sleep(interval)
                print(f"Verify code not found, retrying {15 - retry}")
        return sms_code
