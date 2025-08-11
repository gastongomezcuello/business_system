import hashlib


def generate_numeric_hash(id):
    hash_val = int(hashlib.sha1(str(id).encode()).hexdigest(), 16)
    return str(hash_val)[-10:]
