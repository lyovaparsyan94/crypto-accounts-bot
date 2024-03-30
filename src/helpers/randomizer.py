import random
import string
from random import choice

import names
from credit_card_info_generator import generate_credit_card
from faker import Faker


def generate_root_name():
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


def generate_first_last_name():
    first_name = names.get_first_name(gender='male')
    last_name = names.get_first_name(gender='male')
    return first_name, last_name


def generate_cardholder_name():
    cardholder_name = names.get_full_name()
    return cardholder_name


def generate_card_data():
    card_choice = random.choice(['Visa'])
    card_data = generate_credit_card(card_choice)
    return card_data


def generate_random_addresses():
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
