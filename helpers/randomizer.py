import string
from random import choice


def generate_root_name():
    password = ''
    size = 25
    for i in range(size + 1):
        select = choice(string.ascii_uppercase)
        password += select
    for i in range(size + 1):
        select = choice(string.ascii_lowercase)
        password += select
    for i in range(3):
        select = choice(string.digits)
        password += select
    for i in range(3):
        select = choice(string.punctuation)
        password += select
    print(f'generated root name: {password}')
    return password