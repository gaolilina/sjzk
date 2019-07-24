from django import forms

from modellib.models import CMSRole
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args
from util.decorator.permission import cms_permission


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
        CMSRole.objects.create(name=name, category=category, enable=enable, level=request.user.role.level + 1)
        return self.success()
