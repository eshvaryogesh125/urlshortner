'''helper functions'''
import random, string

def generate_unique_code(length=8):
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return code


