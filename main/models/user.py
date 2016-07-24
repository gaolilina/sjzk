import hashlib
from datetime import datetime

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.db import models

from ChuangYi.settings import IMAGE_PATH, PRIVATE_IMAGE_PATH
from ..models import EnabledManager


__all__ = ['User']


class User(models.Model):
    """用户模型"""

    is_enabled = models.BooleanField(default=True, db_index=True)
    username = models.CharField(max_length=20, default=None, null=True, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField( max_length=11, unique=True)
    token = models.CharField(max_length=32, unique=True)
    time_created = models.DateTimeField(default=datetime.now, db_index=True)

    name = models.CharField(max_length=15, db_index=True)
    description = models.CharField(max_length=100, default='')
    icon = models.ImageField(db_index=True, upload_to=IMAGE_PATH)
    gender = models.CharField(max_length=1, default='')
    qq = models.CharField(max_length=20, default='')
    wechat = models.CharField(max_length=20, default='')
    email = models.EmailField(default='')
    birthday = models.DateField(default=None, null=True, db_index=True)
    province = models.CharField(max_length=20, default='', db_index=True)
    city = models.CharField(max_length=20, default='', db_index=True)
    county = models.CharField(max_length=20, default='', db_index=True)

    is_verified = models.BooleanField(default=False, db_index=True)
    real_name = models.CharField(max_length=20, default='', db_index=True)
    id_number = models.CharField(max_length=18, default='', db_index=True)
    id_card = models.ImageField(upload_to=PRIVATE_IMAGE_PATH)

    is_role_verified = models.BooleanField(default=False, db_index=True)
    role = models.CharField(max_length=20, default='', db_index=True)
    other_number = models.CharField(max_length=20, default='')
    other_card = models.ImageField(upload_to=PRIVATE_IMAGE_PATH)
    # 学校或公司
    unit1 = models.CharField(max_length=20, default='')
    # 学院或子部门
    unit2 = models.CharField(max_length=20, default='')
    # 专用或职业
    profession = models.CharField(max_length=20, default='')

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'user'
        ordering = ['-time_created']

    def set_password(self, password):
        hasher = PBKDF2PasswordHasher()
        self.password = hasher.encode(password, hasher.salt())

    def check_password(self, password):
        hasher = PBKDF2PasswordHasher()
        return hasher.verify(password, self.password)

    def update_token(self):
        random_content = self.user.phone_number + datetime.now().isoformat()
        hasher = hashlib.md5()
        hasher.update(random_content.encode())
        self.token = hasher.hexdigest()
