import hashlib


def md5(msg):
    hasher = hashlib.md5()
    hasher.update(msg.encode())
    return hasher.hexdigest()
