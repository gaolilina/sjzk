import hashlib

from django.db import models
from django.utils import timezone

from util.auth import generate_psd
from ..models import EnabledManager

__all__ = ['AdminUser']


class AdminUser(models.Model):
    """用户模型"""

    is_enabled = models.BooleanField(default=True, db_index=True)
    username = models.CharField(max_length=20, unique=True, db_index=True)
    password = models.CharField(max_length=128)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # 角色，弃用，以后使用 system_role 那套系统
    # a - 竞赛, b - 活动, c - 广告, x - 运营 , y - 管理, z - 超级管理
    role = models.CharField(default='', max_length=26)
    # 系统角色
    system_role = models.ForeignKey('modellib.CMSRole', related_name='users', default=None, null=True)
    # token
    token = models.CharField(max_length=254, default='')

    name = models.CharField(max_length=15, default='', db_index=True)
    icon = models.CharField(max_length=100, default='')
    gender = models.CharField(max_length=1, default='')
    email = models.EmailField(default='')
    phone_number = models.CharField(max_length=11, default='')
    qq = models.CharField(max_length=20, default='')
    wechat = models.CharField(max_length=20, default='')

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'admin_user'
        ordering = ['-time_created']

    ###########################################以下弃用
    def save_and_generate_name(self):
        """保存当前实例并生成序列用户名"""

        self.name = '智库后台用户 #{}'.format(self.id)
        self.save()

    def can_a(self):
        return self.premission_chk('a')

    def can_b(self):
        return self.premission_chk('b')

    def can_x(self):
        return self.premission_chk('x')

    def can_y(self):
        return self.premission_chk('y')

    def can_z(self):
        return self.premission_chk('z')

    def premission_chk(self, target):
        """ 检查权限 """
        if target == "z":
            if 'z' in self.role:
                return True
        elif target == 'y':
            if 'y' in self.role or 'z' in self.role:
                return True
        elif target == 'x':
            if 'x' in self.role or 'y' in self.role or 'z' in self.role:
                return True
        else:
            if 'x' in self.role or 'y' in self.role or 'z' in self.role:
                return True
            elif target in self.role:
                return True
        return False

    def set_password(self, password):
        """弃用，设置密码"""
        self.password = generate_psd(password)

    def check_password(self, password):
        """弃用，检查密码"""

        return self.password == generate_psd(password)

    def update_token(self):
        """弃用，更新用户令牌"""

        random_content = self.phone_number + timezone.now().isoformat()
        hasher = hashlib.md5()
        hasher.update(random_content.encode())
        AdminUser.objects.filter(id=self.id).update(token=hasher.hexdigest())
