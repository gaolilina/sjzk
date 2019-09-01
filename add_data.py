# coding:utf-8
import django
import os

from django.contrib.auth.hashers import PBKDF2PasswordHasher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChuangYi.settings")

if django.VERSION >= (1, 7):  # 自动判断版本
    django.setup()


def add_illegal_word():
    """添加系统过滤词数据"""
    from main.models import IllegalWord
    filename = 'json_data/illegal_word.txt'
    # 读取过滤词文件中的数据并写入数据库
    with open(filename, 'r', encoding="utf-8") as f:
        for lines in f:
            word = lines.strip()
            if len(word) == 0:
                continue
            if len(word) > 20:
                word = word[:20]
            try:
                IllegalWord.objects.create(word=word)
            except:
                continue
        f.close()


def init_system_params():
    from main.models import System
    System.objects.create()
    from modellib.models.config import ApplicationConfig
    ApplicationConfig.objects.create()
    from modellib.models.config import ServerConfig
    ServerConfig.objects.create()


def add_sys_op():
    from admin.models.admin_user import AdminUser
    user = AdminUser(username='admin')
    hasher = PBKDF2PasswordHasher()
    user.password = hasher.encode('cyadmin', hasher.salt())
    user.phone_number = '18301018512'
    user.role = 'z'
    user.name = 'admin'
    from modellib.models.control.system_role import CMSRole
    role = CMSRole(id=CMSRole.ID_ADMIN, name='admin', enable=True, category='admin', level=0)
    role.save()
    user.system_role = role
    user.save()


if __name__ == "__main__":
    add_illegal_word()
    init_system_params()
    add_sys_op()
