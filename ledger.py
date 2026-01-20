import hashlib
import datetime

def generate_hash(prev_hash, voter_roll, timestamp):
    data = f"{prev_hash}{voter_roll}{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
