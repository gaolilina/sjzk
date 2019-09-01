'''
统一 token 规范
'''
import hashlib

from django.utils import timezone


def generate_token(msg):
    random_content = msg + timezone.now().isoformat()
    hasher = hashlib.md5()
    hasher.update(random_content.encode())
    return hasher.hexdigest()
