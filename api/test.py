from string import ascii_lowercase, ascii_uppercase, punctuation, digits
from itertools import product
import string
import random

minimum_length = 2
maximum_length = 2

ALLOWED_CHARACTERS = ascii_lowercase

count = 0

for length in range(minimum_length, maximum_length + 1):
    for combo in product(ALLOWED_CHARACTERS, repeat=length):
        print(''.join(combo))
        count=count+1

print(str(count))


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

print(get_random_string(2))