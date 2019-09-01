'''
统一 token 规范
'''

from django.utils import timezone

from util.security import md5


def generate_token(msg):
    random_content = msg + timezone.now().isoformat()
    return md5(random_content)


def generate_psd(psd):
    return md5(psd)
