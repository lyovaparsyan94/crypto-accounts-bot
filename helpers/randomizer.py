import string
from random import choice


def generate_root_name():
    password = ''
    size = 4
    for i in range(size + 1):
        select = choice(string.ascii_uppercase)
        password += select
    for i in range(size + 1):
        select = choice(string.ascii_lowercase)
        password += select
    for i in range(5):
        select = choice('(){}@!#-+=[]')
        password += select
    # for i in range(size + 1):
    #     select = choice(string.digits)
    #     password += select
    return password