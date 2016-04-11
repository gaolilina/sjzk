import datetime
import hashlib

from django.contrib.auth.hashers import PBKDF2PasswordHasher as Hasher
from django.db import models
from django.utils import timezone


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
    APP用户基本信息

    以手机号与IMEI作为默认用户身份标识，用户名、密码默认为空

    """
    phone_number = models.CharField('手机号', max_length=11, unique=True)
    username = models.CharField(
        '用户名', max_length=20,
        default=None, blank=True, null=True, unique=True)
    password = models.CharField('密码', max_length=128, db_index=True)

    name = models.CharField('昵称', max_length=20, db_index=True)
    email = models.EmailField(
        '电子邮箱', default=None, blank=True, null=True, unique=True)

    is_enabled = models.BooleanField('是否有效', default=True, db_index=True)

    create_time = models.DateTimeField('注册时间', default=timezone.now)
    last_active_time = models.DateTimeField(
        '最后一次活动时间', default=None, blank=True, null=True)

    objects = models.Manager()
    enabled = EnabledUserManager()
    disabled = DisabledUserManager()

    class Meta:
        db_table = 'user'

    def __repr__(self):
        return '<User - %s (%s)>' % (self.name, self.phone_number)

    def set_password(self, password):
        """
        利用Django的PBKDF2PasswordHasher对用户密码进行加密
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


class UserToken(models.Model):
    """
    APP用户令牌

    """
    user = models.OneToOneField(User, models.CASCADE, related_name='token_info')

    token = models.CharField('APP密钥', max_length=32, unique=True)
    expire_time = models.DateTimeField('到期时间')

    class Meta:
        db_table = 'user_token'

    def __repr__(self):
        return '<User Token - %s (%s)>' % (
            self.user.name, self.user.phone_number)

    def update(self, available_days=7):
        """
        利用用户手机号与当前时间戳更新APP密钥

        :param available_days: 令牌有效天数，默认为7天

        """
        hasher = hashlib.md5()
        content = self.user.phone_number + str(timezone.now().timestamp())
        hasher.update(content.encode('ascii'))
        self.token = hasher.hexdigest()
        self.expire_time = timezone.now() + datetime.timedelta(available_days)
        self.save()
