from django import forms

from admin.models import AdminUser
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class AllAdminUserList(BaseView):
    @cms_auth
    @cms_permission('filterAllAdminUser')
    @validate_args({
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
        'username': forms.CharField(max_length=100, required=False),
        'name': forms.CharField(max_length=100, required=False),
        'phone': forms.CharField(max_length=100, required=False),
        'role_id': forms.IntegerField(required=False),
    })
    def get(self, request, name='', phone='', username='', role_id=None, page=0, limit=CONSTANT_DEFAULT_LIMIT,
            **kwargs):
        # 构造筛选参数
        filter_params = {}
        if name:
            filter_params['name__icontains'] = name
        if phone:
            filter_params['phone_number__contains'] = phone
        if username:
            filter_params['username__icontains'] = username
        # role_id 小于0 表示筛选无角色的用户
        if role_id is not None:
            if role_id < 0:
                filter_params['system_role__isnull'] = True
            else:
                filter_params['system_role_id'] = role_id
        # 开始筛选
        qs = AdminUser.objects.filter(**filter_params)
        total_count = qs.count()
        users = []
        if total_count > 0:
            users = qs[page * limit:(page + 1) * limit]
        return self.success({
            'totalCount': total_count,
            'list': [adminuser_to_json(u) for u in users]
        })


class AdminUserDetail(BaseView):
    @cms_auth
    @cms_permission('adminuserDetail')
    @validate_args({
        'user_id': forms.IntegerField(required=False),
    })
    @fetch_object(AdminUser.objects, 'user')
    def get(self, request, user, **kwargs):
        return self.success(adminuser_to_json(user))


def adminuser_to_json(u):
    role_json = None
    if u.system_role is not None:
        role = u.system_role
        role_json = {
            'id': role.id,
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
