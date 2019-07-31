# 第一句话一定要引入这个，不能没有
import recommend

# TODO 下面你可以做任何你想做的事情
from admin.models import AdminUser


def adminuser_to_json(u):
    role_json = None
    if u.system_role is not None:
        role = u.system_role
        role_json = {
            'name': role.name,
            'enable': role.enable,
            'category': role.category
        }
    return {
        'id': u.id,
        'username': u.username,
        'enable': u.is_enabled,
        'name': u.name,
        'phone': u.phone_number,
        'gender': u.gender,
        'icon': u.icon,
        'email': u.email,
        'role': role_json
    }


users = AdminUser.objects.all()
for u in users:
    print(adminuser_to_json(u))
