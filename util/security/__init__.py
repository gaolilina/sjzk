import hashlib

hasher = hashlib.md5()


def md5(msg):
    hasher.update(msg.encode())
    return hasher.hexdigest()
