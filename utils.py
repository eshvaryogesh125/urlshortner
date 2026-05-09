'''helper functions'''
import random, string
import threading, os
from dotenv import load_dotenv

import models
load_dotenv()
from time import time
from models import URL

BASE62 = string.digits + string.ascii_letters
MACHINE_ID = int(os.getenv("MACHINE_ID", "1"))
CACHE = {}

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
            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate code.")

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

def check_short_url_exists(db, short_code):
    return db.query(URL).filter_by(short_code=short_code).first()

def create_url_db(db, original_url, short_code):
    new_url = URL(
        original_url=original_url,
        short_code=short_code
    )
    db.add(new_url)
    db.flush() 
    
    new_click = models.Click(url_id=new_url.id)
    db.add(new_click)
    
    db.commit()
    db.refresh(new_url)
    
    return new_url


def get_cache(short_code):
    print(f"Checking cache for {short_code}, Current cache state: {CACHE}")
    if short_code in CACHE:
        original_url, expiry = CACHE[short_code]
        if time() > expiry:
            del CACHE[short_code]
            return None
        return original_url
    return None

def set_cache(short_code, original_url, ttl=600):
    expiry = time() + ttl
    CACHE[short_code] = (original_url, expiry)