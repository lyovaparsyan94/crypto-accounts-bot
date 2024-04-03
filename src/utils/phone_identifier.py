import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code


def get_country_code(phone: str) -> str:
    """
    Get the country code for the given phone number.

    Args:
        phone (str): The phone number to parse.

    Returns:
        str: The country code for the phone number.
    """
    phone_humber = phonenumbers.parse(phone)
    return region_code_for_country_code(phone_humber.country_code)


def get_national_number(phone: str) -> str:
    """
    Get the national number for the given phone number.

    Args:
        phone (str): The phone number to parse.

    Returns:
        str: The national number for the phone number.
    """
    number = phonenumbers.parse(phone)
    str_number = f"{number.national_number}"
    return str_number
