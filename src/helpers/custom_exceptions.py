from config import configs
aws_configs = configs.aws_configs
CARD_LIMIT = aws_configs.CARD_LIMIT
EMAIL_LIMIT = aws_configs.EMAIL_LIMIT


class EmailUsageLimitExceeded(Exception):
    """
    Custom exception raised when an email usage limit is exceeded.

    Attributes:
        email (str): The email address that exceeded the usage limit.
        message (str): The error message.
    """

    def __init__(self, email: str):
        self.email = email
        self.message = f"Email {email} has been used more than {EMAIL_LIMIT} times. Cannot proceed."

    def __str__(self) -> str:
        """
        Return the error message as a string.

        Returns:
            str: The error message.
        """
        return self.message


class CardUsageLimitExceeded(Exception):
    """
    Custom exception raised when an card usage limit is exceeded.

    Attributes:
        card (str): The card address that exceeded the usage limit.
        message (str): The error message.
    """

    def __init__(self, card: str):
        self.email = card
        self.message = f"Card {card} has been used more than {CARD_LIMIT} times. Cannot proceed."

    def __str__(self) -> str:
        """
        Return the error message as a string.

        Returns:
            str: The error message.
        """
        return self.message
