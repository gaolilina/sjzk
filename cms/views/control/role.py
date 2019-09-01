from django import forms

from cms.util.decorator.permission import cms_permission_role
from cms.util.role import role_to_json, get_all_child_role
from modellib.models import CMSRole
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class AllRoleList(BaseView):

    @cms_auth
    @cms_permission('allRoleList')
    @validate_args({
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
        'category': forms.CharField(max_length=100, required=False),
    })
    def get(self, request, category=None, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        filter_param = {}
        if category is not None:
            filter_param['category'] = category
        qs = CMSRole.objects.filter(**filter_param)
        total_count = qs.count()
        roles = qs[page * limit:(page + 1) * limit]
        return self.success({
            'totalCount': total_count,
            'list': [role_to_json(r) for r in roles]
        })

    @cms_auth
    @cms_permission('createRole')
    @validate_args({
        'name': forms.CharField(max_length=100),
        'category': forms.CharField(max_length=100, required=False),
        'enable': forms.NullBooleanField(required=False)
    })
    def post(self, request, name, category='', enable=False, **kwargs):
        CMSRole.objects.create(name=name, category=category, enable=enable,
                               level=request.user.system_role.level + 1,
                               parent_role=request.user.system_role)
        return self.success()


class MyRoleList(BaseView):

    @cms_auth
    @validate_args({
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
        'category': forms.CharField(max_length=100, required=False),
    })
    def get(self, request, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        # 获取我的角色列表
        my_role = request.user.system_role
        filter_param = {}
        if 'category' in kwargs:
            filter_param['category'] = kwargs['category']
        roles = get_all_child_role(my_role, **filter_param)

        return self.success({
            'totalCount': len(roles),
            'list': [role_to_json(r) for r in roles[page * limit:(page + 1) + limit]]
        })


class RoleDetail(BaseView):

    @cms_auth
    @cms_permission('roleDetail')
    @validate_args({
        'role_id': forms.IntegerField(),
    })
    @fetch_object(CMSRole.objects, 'role')
    def get(self, request, role, **kwargs):
        return self.success(role_to_json(role))

    @cms_auth
    @cms_permission('updateRoleInfo')
    @validate_args({
        'role_id': forms.IntegerField(),
        'name': forms.CharField(max_length=100, required=False),
        'category': forms.CharField(max_length=100, required=False),
        'enable': forms.NullBooleanField(required=False)
    })
    @fetch_object(CMSRole.objects, 'role')
    @cms_permission_role()
    def post(self, request, role, **kwargs):
        params_list = ['name', 'category', 'enable']
        update_param = {}
        for p in params_list:
            if p in kwargs:
                update_param[p] = kwargs[p]
        if len(update_param) > 0:
            CMSRole.objects.filter(id=role.id).update(**update_param)
        return self.success()
