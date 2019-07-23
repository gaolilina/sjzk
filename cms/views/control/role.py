from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from util.decorator.param import validate_args
from modellib.models import CMSRole
from util.decorator.auth import cms_auth
from util.decorator.permission import cms_permission


class RoleList(View):

    @cms_auth
    @cms_permission('roleList')
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        qs = CMSRole.objects.all()
        totalCount = qs.count()
        roles = qs[offset:offset + limit] if totalCount > limit else qs
        return JsonResponse({
            'totalCount': totalCount,
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
        return JsonResponse({
            'code': 0
        })
