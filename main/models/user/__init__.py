import hashlib
from datetime import datetime, timedelta

from django.contrib.auth.hashers import PBKDF2PasswordHasher as Hasher
from django.db import models, transaction

from ChuangYi.settings import IMAGE_PATH, PRIVATE_IMAGE_PATH
from main.models.mixins import IconMixin, CountMixin


class EnabledUserManager(models.Manager):
    def get_queryset(self):
        return super(EnabledUserManager, self).get_queryset().filter(
            is_enabled=True)

    def create_user(self, phone_number, password=None, **kwargs):
        """
        建立用户模型与其他相关模型

        :param phone_number: 手机号
        :param password: 密码
        :param kwargs: 其他用户模型相关的关键字参数

        """
        with transaction.atomic():
            user = self.create(phone_number=phone_number, **kwargs)
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

    def create_validated_user(self, phone_number, password=None, **kwargs):
        """
        建立测试用用户（已验证）

        """
        with transaction.atomic():
            user = self.create(phone_number=phone_number, **kwargs)
            if password:
                user.set_password(password)
            user.save()
            if 'name' not in kwargs:
                user.name = '创易用户 %s' % user.id
                user.save(update_fields=['name'])
            token = UserToken(user=user)
            token.update()
            profile = UserProfile(user=user, is_validated=True)
            profile.save()
            identification = UserIdentification(user=user)
            identification.save()
        return user


class DisabledUserManager(models.Manager):
    def get_queryset(self):
        return super(DisabledUserManager, self).get_queryset().filter(
            is_enabled=False)


class User(models.Model, IconMixin, CountMixin):
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
        '头像', db_index=True, upload_to=IMAGE_PATH)
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
        content = self.user.phone_number + datetime.now().isoformat()
        md5 = hashlib.md5()
        md5.update(content.encode())
        self.value = md5.hexdigest()
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
    role = models.CharField(
        '认证身份', max_length=15, default='', db_index=True)
    id_number = models.CharField(
        '身份证号', max_length=18, default='', db_index=True)
    id_card = models.ImageField(
        '身份证照片', db_index=True, upload_to=PRIVATE_IMAGE_PATH)
    other_number = models.CharField(
        '其他证件号码', max_length=18, default='', db_index=True)
    other_card = models.ImageField(
        '其他证件照片', db_index=True, upload_to=PRIVATE_IMAGE_PATH)
    school = models.CharField(
        '学校/单位', max_length=20, default='', db_index=True)
    academy = models.CharField(
        '学院', max_length=20, default='', db_index=True)
    profession = models.CharField(
        '专业/职业', max_length=20, default='', db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    class Meta:
        db_table = 'user_identification'
