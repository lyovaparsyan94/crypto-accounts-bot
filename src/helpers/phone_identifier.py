import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code


def get_country_code(phone):
    phone_humber = phonenumbers.parse(phone)
    return region_code_for_country_code(phone_humber.country_code)


def get_national_number(phone):
    number = phonenumbers.parse(phone)
    return f"{number.national_number}"
