import random
from datetime import datetime


def encrypt_phone_number(n):
    """
    '加密' 手机号

    生成随机三位数XXX（不小于100）、随机三位数YY（不小于100）

    其中XXX与手机号后四位进行拼接，
    假设手机号后四位为WWWW，拼接方式为：WXWXWXW

    拼接后得到的数字WXWXWXW模YYY得到ZZZ（位数不够则补零）

    使用以上数字生成字符串：'XXX[手机号前3位]YYY[手机号后8位]ZZZ'

    将得到的字符串与密钥做异或运算，返回 '加密' 后的数据

    :param n: 11位手机号字符串
    :return: '加密' 后的字符串

    """
    x = str(random.randrange(100, 1000))
    y = str(random.randrange(100, 1000))
    m = n[-4] + x[-3] + n[-3] + x[-2] + n[-2] + x[-1] + n[-1]
    z = str(int(m) % int(y))
    while len(z) < 3:
        z = '0' + z
    raw_str = x + n[:3] + y + n[-8:] + z

    # 密钥为 <2048-10-24 5:12:00> 时间戳及其除以二得到的数字拼接得到的字符串
    d1 = int(datetime(2048, 10, 24, 5, 12).timestamp())
    d2 = int(d1 / 2)
    key = str(d1) + str(d2)

    return str(int(raw_str) ^ int(key))


def decrypt_phone_number(s):
    """
    '解密' 手机号

    :param s: '加密' 后的字符串
    :return: 11位手机号

    """
    d1 = int(datetime(2048, 10, 24, 5, 12).timestamp())
    d2 = int(d1 / 2)
    key = str(d1) + str(d2)

    raw_str = str(int(s) ^ int(key))

    x = raw_str[:3]
    y = raw_str[6:9]
    z = raw_str[-3:]
    n = raw_str[3:6] + raw_str[9:17]
    m = n[-4] + x[-3] + n[-3] + x[-2] + n[-2] + x[-1] + n[-1]

    if int(m) % int(y) != int(z):
        raise ValueError('invalid phone information')

    return n
