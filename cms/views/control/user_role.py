from django import forms

from admin.models import AdminUser
from cms.util.decorator.permission import cms_permission_user
from modellib.models import CMSRole
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class ManageUserRole(BaseView):
    @cms_auth
    @cms_permission('assignUserRole')
    @validate_args({
        'user_id': forms.CharField(max_length=100),
        'role_id': forms.IntegerField(),
    })
    @fetch_object(AdminUser.objects, 'user')
    @fetch_object(CMSRole.objects, 'role')
    @cms_permission_user()
    def post(self, request, user, role, **kwargs):
        # 为用户分配角色
        AdminUser.objects.filter(username=user.username).update(system_role=role)
        return self.success()

    @cms_auth
    @cms_permission('removeUserRole')
    @validate_args({
        'user_id': forms.CharField(max_length=100),
    })
    @fetch_object(AdminUser.objects, 'user')
    @cms_permission_user()
    def delete(self, request, user, **kwargs):
        # 没有分配角色，直接成功
        if user.system_role is None:
            return self.success()
        # 清除角色
        AdminUser.objects.filter(username=user.username).update(system_role=None)
        return self.success()
