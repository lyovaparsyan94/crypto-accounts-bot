import json

from config import configs
from logs.aws_logger import awslogger

aws_configs = configs.aws_configs
CARD_LIMIT = aws_configs.CARD_LIMIT
EMAIL_LIMIT = aws_configs.EMAIL_LIMIT
MANDATORY_FIELDS = aws_configs.MANDATORY_FIELDS
PATH_TO_SAVE = configs.dir_configs.PATH_TO_SAVE
PHONE_LIMIT = aws_configs.PHONE_LIMIT
REQUIRED_FIELDS = aws_configs.REQUIRED_FIELDS
from utils.custom_exceptions import CardUsageLimitExceeded, EmailUsageLimitExceeded


class FileHandler:

    def get_limit(self, value: str, field: str = 'cards') -> int:
        """
        Get the usage limit for a specific value in the given field.

        Args:
            value (str): The value to check the usage limit for.
            field (str, optional): The field to check the usage limit in (default is 'cards').

        Returns:
            int: The usage limit for the specified value in the given field.
        """
        data = self.get_current_data()
        result = None
        if field in MANDATORY_FIELDS:
            data_of_field = data.get(f'used_{field}_count', False)
            used_times = data_of_field.get(value, 0)
            if isinstance(used_times, int):
                result = used_times
        return result

    def is_possible_to_use(self, value: str, field: str = 'cards') -> int | None:
        """
        Check if it is possible to use the specified value in the given field.

        Args:
            value (str): The value to check.
            field (str, optional): The field to check (default is 'cards').

        Returns:
            bool | None: True if it is possible to use the value, False otherwise. None if the field is invalid.
        """
        limit = self.get_limit(value=value, field=field)
        if field == "cards":
            return limit < CARD_LIMIT
        elif field == "phones":
            return limit < PHONE_LIMIT
        elif field == "emails":
            return limit < EMAIL_LIMIT

    def get_current_data(self, filename: str = PATH_TO_SAVE) -> dict:
        """load file from current json file into dict, by default from PATH_TO_SAVE, configured from constants"""
        with open(fr"{filename}") as file:
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
                "card": "",
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
        Updates AWS user information based on the provided field and value.

        Args:
            root_password (str): The root password for authentication.
            field (str): The field to update (e.g., 'phone', 'email', 'card').
            value (str): The new value for the specified field.

        Notes:
            - Values 'phone', 'email', and 'card' are mandatory to check, as they have usage limits set from constants.
            - The method updates the user information if the conditions are met.
        """
        info_updated = False
        current_data = self.get_current_data()
        user = current_data['users'][0]
        if field not in REQUIRED_FIELDS:
            awslogger.log_critical(f'field {field} not found')
            raise ValueError(f'field {field} not found ')

        mandatory_field = f"{field}s"
        if mandatory_field not in MANDATORY_FIELDS:
            user[root_password][field] = value
            info_updated = True
        elif self.is_possible_to_use(value=value, field=mandatory_field):
            data_of_field = current_data.get(f'used_{mandatory_field}_count', False)
            used_times = data_of_field.get(value, 0)
            if isinstance(used_times, int):
                updated_times_used = used_times + 1
                current_data[f'used_{mandatory_field}_count'][value] = updated_times_used
                user[root_password][field] = value
                info_updated = True

        if info_updated:
            self.save_data(data=current_data)

    def save_data(self, data: dict, filename: str = PATH_TO_SAVE) -> None:
        """
        Save data in JSON format to a file.

        Args:
            data (dict): The data to be saved.
            filename (str, optional): The name of the file (default: PATH_TO_SAVE).

        Returns:
            None
        """
        with open(f"{filename}", 'w') as file:
            json.dump(data, file, indent=2)

    def validate_email(self, email: str) -> bool:
        """
        Validate an email address and check if it exceeds the usage limit.

        Args:
            email (str): The email address to validate.

        Raises:
            EmailUsageLimitExceeded: If the email usage limit is exceeded.

        Returns:
            bool: True if the email is valid and within the usage limit, False otherwise.
        """
        if email and not self.is_possible_to_use(field='emails', value=email):
            raise EmailUsageLimitExceeded(email)
        return True

    def validate_card(self, card: str) -> bool:
        """
        Validate a card number and check if it exceeds the usage limit.

        Args:
            card (str): The card number to validate.

        Raises:
            CardUsageLimitExceeded: If the card usage limit is exceeded.

        Returns:
            bool: True if the card is valid and within the usage limit, False otherwise.
        """
        if card and not self.is_possible_to_use(field='cards', value=card):
            raise CardUsageLimitExceeded(card)
        return True

    def validate_card_and_email(self, card: str, email: str) -> None:
        """
        Validate both a card number and an email address.

        Args:
            card (str): The card number to validate.
            email (str): The email address to validate.

        Notes:
            - Calls the validate_email and validate_card methods.
        """
        self.validate_email(email)
        self.validate_card(card)
        awslogger.log_info(f'{card} and {email} validated')
