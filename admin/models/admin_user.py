import hashlib

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.db import models
from django.utils import timezone

from ..models import EnabledManager


__all__ = ['AdminUser']


class AdminUser(models.Model):
    """用户模型"""

    is_enabled = models.BooleanField(default=True, db_index=True)
    username = models.CharField(max_length=20, unique=True, db_index=True)
    password = models.CharField(max_length=128)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # a - 竞赛, b - 活动, y - 运维, z - 管理
    role = models.CharField(default='', max_length=26)

    name = models.CharField(max_length=15, default='', db_index=True)
    description = models.CharField(max_length=100, default='')
    icon = models.CharField(max_length=100, default='')
    gender = models.CharField(max_length=1, default='')
    email = models.EmailField(default='')
    phone_number = models.CharField(max_length=11, default='')

    is_verified = models.BooleanField(default=False, db_index=True)
    real_name = models.CharField(max_length=20, default='', db_index=True)
    id_number = models.CharField(max_length=18, default='', db_index=True)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'admin_user'
        ordering = ['-time_created']

    def set_password(self, password):
        """设置密码"""

        hasher = PBKDF2PasswordHasher()
        self.password = hasher.encode(password, hasher.salt())

    def check_password(self, password):
        """检查密码"""

        hasher = PBKDF2PasswordHasher()
        return hasher.verify(password, self.password)

    def save_and_generate_name(self):
        """保存当前实例并生成序列用户名"""

        self.save()
        self.name = '创易汇后台用户 #{}'.format(self.id)
        self.save()
