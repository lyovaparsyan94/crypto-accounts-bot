import json
from configs.constants import PHONE_LIMIT, EMAIL_LIMIT, CARD_LIMIT, AWS_FILENAME


class FileHandler:
    def __init__(self):
        self.phone_limit = PHONE_LIMIT
        self.mail_limit = EMAIL_LIMIT
        self.card_limit = CARD_LIMIT

    def save_data(self, data):
        with open('aws_registered_users.json', 'w') as file:
            json.dump(data, file, indent=2)

    def check_limits(self, email, phone, card):



users = {
    "users": [
        {
            "card": "1025 1202 1245 9548",
            "valid_date": "10/25",
            "cvv": "455",
            "cardholder": "Pol Walker",
            "phone": "+37477151210",
            "full_name": "Pol Walker",
            "email": "regmail@gmail.com",
            "root_pass": "root@password#~",
            "account_name": "berklay123",
            "address": "11 Virginia St, Richmond, VA, 22314, USA"
        },
        {
            "card": "1025 1202 1245 9548",
            "valid_date": "09/24",
            "cvv": "789",
            "cardholder": "Jane Doe",
            "phone": "+14155551234",
            "full_name": "Jane Doe",
            "email": "jane.doe@email.com",
            "root_pass": "secureRootPass123",
            "account_name": "janedoe123",
            "address": "123 Main St, Anytown, CA, 98765, USA"
        },
        {
            "card": "9876 5432 1098 7654",
            "valid_date": "03/27",
            "cvv": "246",
            "cardholder": "Alex Smith",
            "phone": "+442071234567",
            "full_name": "Alex Smith",
            "email": "alex.smith@example.com",
            "root_pass": "mySecretRootPass",
            "account_name": "asmith123",
            "address": "456 Elm St, London, NW1 7RG, UK"
        },
    ],
    'used_phones_count': {"+442071234567": 4, "+442071214567": 3, "+442071214167": 6},
    'used_cards_count': {"9876 5432 1098 7654": 1, "9876 5432 3645 7654": 3, "9876 5432 1098 1478": 8}

}

file_handler = FileHandler()
