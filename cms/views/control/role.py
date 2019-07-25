from django import forms

from modellib.models import CMSRole
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission
from cms.util.decorator.permission import cms_permission_role


class RoleList(BaseView):

    @cms_auth
    @cms_permission('roleList')
    @validate_args({
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
    })
    def get(self, request, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        qs = CMSRole.objects.all()
        total_count = qs.count()
        roles = qs[page * limit:(page + 1) * limit]
        return self.success({
            'totalCount': total_count,
            'list': [{
                'name': r.name,
                'enable': r.enable,
                'category': r.category
            } for r in roles]
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


class RoleDetail(BaseView):

    @cms_auth
    @cms_permission('roleDetail')
    @validate_args({
        'role_id': forms.IntegerField(),
    })
    @fetch_object(CMSRole.objects, 'role')
    def get(self, request, role, **kwargs):
        result = {
            'name': role.name,
            'enable': role.enable,
            'category': role.category,
        }
        return self.success(result)

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
