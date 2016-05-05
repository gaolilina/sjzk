import hashlib
import random
from datetime import datetime, timedelta

from django.contrib.auth.hashers import PBKDF2PasswordHasher as Hasher
from django.db import models, transaction


class EnabledUserManager(models.Manager):
    def get_queryset(self):
        return super(EnabledUserManager, self).get_queryset().filter(
            is_enabled=True)


class DisabledUserManager(models.Manager):
    def get_queryset(self):
        return super(DisabledUserManager, self).get_queryset().filter(
            is_enabled=False)


class User(models.Model):
    """
    用户账户信息

    """
    phone_number = models.CharField(
        '手机号', max_length=11, unique=True)
    username = models.CharField(
        '用户名', max_length=15, default=None, null=True, unique=True)
    password = models.CharField(
        '密码', max_length=128, db_index=True)
    name = models.CharField(
        '昵称', max_length=15, db_index=True)
    icon = models.ImageField(
        '用户头像', db_index=True)
    is_enabled = models.BooleanField(
        '是否有效', default=True)
    create_time = models.DateTimeField(
        '注册时间', default=datetime.now, db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    objects = models.Manager()
    enabled = EnabledUserManager()
    disabled = DisabledUserManager()

    class Meta:
        db_table = 'user'

    @property
    def icon_url(self):
        return self.icon.url if self.icon else None

    def set_password(self, password):
        """
        利用 Django 的 PBKDF2PasswordHasher 对用户密码进行加密
        最终密码格式为：<algorithm>$<iterations>$<salt>$<hash>

        :param password: 密码原文

        """
        hasher = Hasher()
        self.password = hasher.encode(password, hasher.salt())

    def check_password(self, password):
        """
        校验密码

        :param password: 密码原文
        :return: True | False

        """
        hasher = Hasher()
        return hasher.verify(password, self.password)

    @classmethod
    def create(cls, phone_number, password=None, **kwargs):
        """
        建立用户模型与其他相关模型

        :param phone_number: 手机号
        :param password: 密码
        :param kwargs: 其他用户模型相关的关键字参数

        """
        with transaction.atomic():
            user = cls(phone_number=phone_number, **kwargs)
            if password:
                user.set_password(password)
            user.save()
            if 'name' not in kwargs:
                user.name = '创易用户 %s' % user.id
                user.save(update_fields=['name'])
            token = UserToken(user=user)
            token.update()
            profile = UserProfile(user=user)
            profile.save()
            identification = UserIdentification(user=user)
            identification.save()
        return user

    @staticmethod
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

    @staticmethod
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


class UserToken(models.Model):
    """
    用户令牌

    """
    user = models.OneToOneField(User, models.CASCADE, related_name='token')

    value = models.CharField('令牌', max_length=32, unique=True)
    expire_time = models.DateTimeField('到期时间', db_index=True)

    class Meta:
        db_table = 'user_token'

    def update(self, available_days=7):
        """
        利用用户手机号与当前时间计算并更新APP密钥

        :param available_days: 令牌有效天数，默认为7天

        """
        hasher = hashlib.md5()
        content = self.user.phone_number + str(datetime.now().isoformat())
        hasher.update(content.encode('ascii'))
        self.value = hasher.hexdigest()
        self.expire_time = datetime.now() + timedelta(available_days)
        self.save()


class UserProfile(models.Model):
    """
    用户个人资料

    """
    user = models.OneToOneField(User, models.CASCADE, related_name='profile')

    description = models.TextField(
        '个人简介', max_length=100, default='', db_index=True)
    email = models.EmailField(
        '电子邮箱', default='', db_index=True)
    gender = models.IntegerField(
        '性别', default=0, choices=(('保密', 0), ('男', 1), ('女', 1)))
    birthday = models.DateField(
        '出生日期', default=None, null=True, db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    class Meta:
        db_table = 'user_profile'


class UserIdentification(models.Model):
    """
    用户身份信息

    """
    user = models.OneToOneField(
        User, models.CASCADE, related_name='identification')

    is_verified = models.BooleanField(
        '是否通过实名验证', default=False)
    name = models.CharField(
        '真实姓名', max_length=15, default='', db_index=True)
    id_number = models.CharField(
        '身份证号', max_length=18, default='', db_index=True)
    id_card_photo = models.ImageField(
        '身份证照片', db_index=True)
    school = models.CharField(
        '所在学校', max_length=20, default='', db_index=True)
    student_number = models.CharField(
        '学生证号', max_length=15, default='', db_index=True)
    student_card_photo = models.ImageField(
        '学生证照片', db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    class Meta:
        db_table = 'user_identification'
