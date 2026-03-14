'''helper functions'''
import random, string
from models import URL

def generate_code(length=8):
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return code


def generate_unique_code(db):
    while True:
        code = generate_code()
        exists = db.query(URL).filter_by(short_code=code).first()

        if not exists:
            return code
