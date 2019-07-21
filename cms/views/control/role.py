from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.utils.decorators import validate_args
from modellib.models import CMSRole
from util.decorator.auth import cms_auth
from util.decorator.permission import cms_permission


class RoleList(View):

    @cms_auth
    @cms_permission('roleList')
    def get(self, request):
        roles = CMSRole.objects.all()
        return JsonResponse({
            'list': [{
                'name': r.name,
                'enable': r.enable,
                'category': r.category
            } for r in roles]
        })

    @validate_args({
        'name': forms.CharField(max_length=100),
        'category': forms.CharField(max_length=100, required=False),
        'enable': forms.NullBooleanField(required=False)
    })
    def post(self, request, name, category='', enable=False, **kwargs):
        CMSRole.objects.create(name=name, category=category, enable=enable, level=request.user.role.level + 1)
        return JsonResponse({})
