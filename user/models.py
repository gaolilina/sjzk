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


class UserProfile(models.Model):
    """
    APP用户基本资料

    """
    user = models.OneToOneField(User, models.CASCADE, related_name='profile')

    description = models.TextField(
        '个人简介', max_length=100, default='', db_index=True)
    gender = models.IntegerField(
        '性别', default=0, choices=(('保密', 0), ('男', 1), ('女', 1)))
    birthday = models.DateField(
        '出生日期', default=None, blank=True, null=True)
    icon = models.ImageField('用户头像')

    class Meta:
        db_table = 'user_profile'

    def __repr__(self):
        return '<User Profile - %s>' % self.user.name


class UserIdentification(models.Model):
    """
    APP用户身份信息

    """
    user = models.OneToOneField(
        User, models.CASCADE, related_name='identification')

    is_verified = models.BooleanField(
        '是否已通过实名认证', default=False, db_index=True)
    name = models.CharField(
        '真实姓名', max_length=10, default='', db_index=True)
    number = models.CharField('身份证号', max_length=18, default='')
    photo = models.ImageField('身份证照片')

    class Meta:
        db_table = 'user_identification'

    def __repr__(self):
        return '<User Identification - %s>' % self.user.name


class UserStudentIdentification(models.Model):
    """
    APP用户学生信息

    """
    user = models.OneToOneField(
        User, models.CASCADE, related_name='student_identification')

    school = models.CharField('学校名称', max_length=20, default='')
    number = models.CharField('学生证号', max_length=20, default='')
    photo = models.ImageField('学生证照片')

    class Meta:
        db_table = 'user_student_identification'

    def __repr__(self):
        return '<User Student Identification - %s>' % self.user.name


class UserEducationExperience(models.Model):
    """
    APP用户教育经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'education_experiences', 'education_experience')

    school = models.CharField('学校', max_length=20, default='')
    degree = models.CharField('学历', max_length=2, default='')
    major = models.CharField('专业', max_length=20, default='')
    begin_time = models.DateField(
        '入学时间', default=None, blank=True, null=True)
    end_time = models.DateField(
        '毕业时间', default=None, blank=True, null=True)

    order = models.IntegerField('序号')

    class Meta:
        db_table = 'user_education_experience'
        ordering = ['order']

    def __repr__(self):
        return '<User Education Experience %s - %s>' % (
            self.order, self.user.name)


class UserFieldworkExperience(models.Model):
    """
    APP用户实习经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'fieldwork_experiences', 'fieldwork_experience')

    company = models.CharField('公司', max_length=20, default='')
    position = models.CharField('职位', max_length=20, default='')
    begin_time = models.DateField(
        '入职时间', default=None, blank=True, null=True)
    end_time = models.DateField(
        '离职时间', default=None, blank=True, null=True)

    order = models.IntegerField('序号')

    class Meta:
        db_table = 'user_fieldwork_experience'
        ordering = ['order']

    def __repr__(self):
        return '<User Fieldwork Experience %s - %s>' % (
            self.order, self.user.name)


class UserWorkExperience(models.Model):
    """
    APP用户工作经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'work_experiences', 'work_experience')

    company = models.CharField('公司', max_length=20, default='')
    position = models.CharField('职位', max_length=20, default='')
    begin_time = models.DateField(
        '入职时间', default=None, blank=True, null=True)
    end_time = models.DateField(
        '离职时间', default=None, blank=True, null=True)

    order = models.IntegerField('序号')

    class Meta:
        db_table = 'user_work_experience'
        ordering = ['order']

    def __repr__(self):
        return '<User Work Experience %s - %s>' % (
            self.order, self.user.name)
