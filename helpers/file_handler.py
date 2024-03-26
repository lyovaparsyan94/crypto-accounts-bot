import json

from configs.constants import (
    AWS_FILENAME,
    CARD_LIMIT,
    DATA_DIR,
    EMAIL_LIMIT,
    MANDATORY_FIELDS,
    PHONE_LIMIT,
    REQUIRED_FIELDS,
)


class FileHandler:
    def __init__(self):
        self.phone_limit = PHONE_LIMIT
        self.mail_limit = EMAIL_LIMIT
        self.card_limit = CARD_LIMIT

    @staticmethod
    def save_data(data: dict, filename: str = AWS_FILENAME) -> None:
        """save data in json, by default in the 'filename' directory configured from constants"""
        with open(fr'{DATA_DIR}/{filename}.json', 'w') as file:
            json.dump(data, file, indent=2)

    def get_limit(self, value: str, field: str = 'cards') -> int:
        """field must be cards or emails or phones"""
        data = self.get_current_data()
        result = None
        if field in MANDATORY_FIELDS:
            data_of_field = data.get(f'used_{field}_count', False)
            used_times = data_of_field.get(value, 0)
            if isinstance(used_times, int):
                result = used_times
        return result

    def is_possible_to_use(self, value: str, field: str = 'cards') -> int | None:
        """checks if value of field not used more than set limit """
        limit = self.get_limit(value=value, field=field)
        if limit or limit == 0:
            if field == "cards":
                return limit < CARD_LIMIT
            elif field == "phones":
                return limit < PHONE_LIMIT
            elif field == "emails":
                return limit < EMAIL_LIMIT
        return None

    @staticmethod
    def get_current_data(filename: str = AWS_FILENAME) -> dict:
        """load file from current json file into dict, by default from AWS_FILENAME, configured from constants"""
        with open(fr'{DATA_DIR}/{filename}.json') as file:
            return json.load(file)

    def create_aws_user_info(self, root_password: str) -> bool:
        """
        Creates AWS user information if it does not already exist with key 'root'

        Returns:
            bool: True if the information was updated, False otherwise.
        """
        info_updated = False
        current_data = self.get_current_data()
        users_info = current_data['users'][0]
        if not users_info.get(root_password):
            users_info[root_password] = {
                "first_name": "",
                "last_name": "",
                "card_number": "",
                "valid_date": "",
                "cvv": "",
                "cardholder": "",
                "phone": "",
                "full_name": "",
                "email": "",
                "root_pass": f"{root_password}",
                "account_name": "",
                "verify_email_code": "",
                "city": "",
                "postal_code": "",
                "country": "",
                "full_address": "",
            }
            info_updated = True
            if info_updated:
                self.save_data(data=current_data)
        return info_updated

    def update_aws_user_info(self, root_password: str, field: str, value: str) -> None:
        """
        Updates AWS user information based on the provided field and value, such us first_name
        values 'phone', 'email', 'card' are madatory to check, as they have using limit, set from constants
        """
        info_updated = False
        current_data = self.get_current_data()
        user = current_data['users'][0]
        if field in REQUIRED_FIELDS:
            mandatory_field = f"{field}s"
            if mandatory_field not in MANDATORY_FIELDS:
                user[root_password][field] = value
                info_updated = True
            else:
                if self.is_possible_to_use(value=value, field=mandatory_field):
                    data_of_field = current_data.get(f'used_{mandatory_field}_count', False)
                    used_times = data_of_field.get(value, 0)
                    if isinstance(used_times, int):
                        updated_times_used = used_times + 1
                        current_data[f'used_{mandatory_field}_count'][value] = updated_times_used
                        user[root_password][field] = value
                        info_updated = True

        if info_updated:
            self.save_data(data=current_data)

