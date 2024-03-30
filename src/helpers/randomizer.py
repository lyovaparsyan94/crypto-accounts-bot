import string
from random import choice

import names
from faker import Faker


def generate_root_name() -> str:
    """
    Generates a random root name.

    Returns:
        str: A random root name.
    """
    password = ''
    size = 24
    for i in range(size):
        if i % 2 == 0:
            select = choice(string.ascii_lowercase)
            password += select
        elif i % 3 == 0:
            select = choice(string.ascii_uppercase)
            password += select
        # elif i % 5 == 0:
        #     select = choice(string.digits)
        #     password += select
        else:
            select = choice('!@#=+-')
            password += select
    print(f'generated root name: {password}')
    return password


def generate_first_last_name() -> tuple:
    """
    Generates a random first name and last name.

    Returns:
        tuple: A tuple containing the first name and last name.
    """
    first_name = names.get_first_name(gender='male')
    last_name = names.get_first_name(gender='male')
    return first_name, last_name


def generate_cardholder_name() -> str:
    """
    Generates a random cardholder name.

    Returns:
        str: A random cardholder name.
    """
    cardholder_name = names.get_full_name()
    return cardholder_name


def generate_card_data() -> str:
    """
    Generates a random cardholder name.

    Returns:
        str: A random cardholder name.
    """
    cardholder_name = names.get_full_name()
    return cardholder_name


def generate_random_addresses() -> dict:
    """
    Generates a random address.

    Returns:
        dict: A dictionary containing address, city, state, postal code, country, and full address in the USA.
    """
    fake = Faker('en_US')
    address = fake.street_address()
    city = fake.city()
    state = fake.state_abbr()
    postal_code = fake.postcode()
    # country = fake.country()
    country = 'United States'
    fake_info = {
        'address': address,
        'city': city,
        'state': state,
        'postal_code': postal_code,
        'country': country,
        "full_address": f"{address},  USA"
    }
    return fake_info
