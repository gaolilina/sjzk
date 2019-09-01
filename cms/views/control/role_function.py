from django import forms

from cms.util.decorator.permission import cms_permission_role, cms_permission_role_function
from cms.util.role import get_all_child_role
from modellib.models import CMSRole, CMSFunction
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class RoleFunction(BaseView):

    @cms_auth
    @cms_permission('roleFunctionList')
    @validate_args({
        'role_id': forms.IntegerField(),
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
        'category': forms.CharField(max_length=100, required=False),
    })
    @fetch_object(CMSRole.objects, 'role')
    def get(self, request, role, category=None, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        filter_param = {}
        if category is not None:
            filter_param['category'] = category
        qs = role.functions.filter(**filter_param)
        total_count = qs.count()
        functions = qs.all()[page * limit:(page + 1) * limit]
        result = {
            'totalCount': total_count,
            'list': [{
                'id': f.id,
                'name': f.name,
                'enable': f.enable,
                'needVerify': f.needVerify,
                'category': f.category,
            } for f in functions]
        }
        return self.success(result)


class ManageRoleFunction(BaseView):

    @cms_auth
    @cms_permission('addRoleFunction')
    @validate_args({
        'role_id': forms.IntegerField(),
        'function_id': forms.CharField(max_length=100),
    })
    @fetch_object(CMSRole.objects, 'role')
    @fetch_object(CMSFunction.objects, 'function')
    @cms_permission_role()
    @cms_permission_role_function()
    def post(self, request, role, function, **kwargs):
        role.functions.add(function)
        return self.success()

    @cms_auth
    @cms_permission('removeRoleFunction')
    @validate_args({
        'role_id': forms.IntegerField(),
        'function_id': forms.CharField(max_length=100),
    })
    @fetch_object(CMSRole.objects, 'role')
    @fetch_object(CMSFunction.objects, 'function')
    @cms_permission_role()
    @cms_permission_role_function()
    def delete(self, request, role, function, **kwargs):
        children = get_all_child_role(role)
        # 先移除子角色的功能
        for r in children:
            r.functions.remove(function)
        # 在移除自己的功能
        role.functions.remove(function)
        return self.success()
