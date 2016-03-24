import random

from ChuangYi import settings


def encrypt_phone_info(phone_number, imei):
    """
    '加密' 手机号与IMEI信息

    生成随机两位数XX（不小于10）、随机一位数Y（非零）与两者的模Z，
    生成以下格式字符串：
        'XX[11位手机号]Y[15位IMEI]Z'
    之后与密钥做异或运算，返回 '加密' 后的数据

    :param phone_number: 11位手机号字符串
    :param imei: 15位IMEI字符串
    :return: '加密' 后的30位字符串

    """
    x = random.randrange(10, 100)
    y = random.randrange(1, 10)
    z = x % y

    # 使用SECRET_KEY转成数字后的前30位作为密钥
    secret_key = ''
    for i in settings.SECRET_KEY:
        secret_key += str(ord(i))
    secret_key = int(secret_key[:30])
    phone_info = int(str(x) + phone_number + str(y) + imei + str(z))

    return str(phone_info ^ secret_key)


def decrypt_phone_info(phone_info):
    """
    '解密' 手机号与IMEI信息

    :param phone_info: '加密' 后的30位字符串
    :return: None | phone_number, imei

    """
    secret_key = ''
    for i in settings.SECRET_KEY:
        secret_key += str(ord(i))
    secret_key = secret_key[:30]
    phone_info = str(int(phone_info) ^ int(secret_key))

    x = phone_info[:2]
    y = phone_info[13]
    z = phone_info[-1]

    if int(x) % int(y) != int(z):
        raise ValueError('invalid phone information')

    return phone_info[2:13], phone_info[14:29]
