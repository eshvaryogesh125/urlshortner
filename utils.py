'''helper functions'''
import random, string
import threading, os
from dotenv import load_dotenv
load_dotenv()
from time import time
from models import URL

BASE62 = string.digits + string.ascii_letters
MACHINE_ID = int(os.getenv("MACHINE_ID", "1"))

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

class CodeGeneratorTimestamp:
    def __init__(self, machine_id=1):
        self.machine_id = machine_id

        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

        self.sequence_bits = 12
        self.machine_bits = 10
        
        self.machine_id_shift = self.sequence_bits
        self.timestamp_shifts = self.sequence_bits + self.machine_bits

        self.max_sequence = (1 << self.sequence_bits) - 1

        self.epoch = 1700000000000

    def _current_timestamp(self):
        return int(time() * 1000)
    
    def generate_code(self):
        with self.lock:
            timestamp = self._current_timestamp()
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence

                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        timestamp = self._current_timestamp()
            else:
                self.sequence = 0

            self.last_timestamp = timestamp
            
            code = ((timestamp - self.epoch) << self.timestamp_shifts) | (self.machine_id << self.machine_id_shift) | self.sequence
            return code

timestamp_code = CodeGeneratorTimestamp(MACHINE_ID)

def encode_base62(num):
    base = 62
    encoded = []

    while num > 0:
        num, rem = divmod(num, base)
        encoded.append(BASE62[rem])

    code = ''.join(reversed(encoded))
    return code

def generate_timestamp_code():
    code = timestamp_code.generate_code()
    return encode_base62(code)
