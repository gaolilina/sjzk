from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from util.decorator.param import validate_args, fetch_object
from modellib.models import CMSFunction
from util.decorator.auth import cms_auth
from util.decorator.permission import cms_permission


class AllFunctionList(View):

    @cms_auth
    @cms_permission('allFunctionList')
    def get(self, request):
        functions = CMSFunction.objects.all()
        result = [{
            'id': f.id,
            'name': f.name,
            'enable': f.enable,
            'needVerity': f.needVerify,
            'category': f.category
        } for f in functions]
        return JsonResponse({
            'code': 0,
            'data': result
        })

    @cms_auth
    @cms_permission('addFunction')
    @validate_args({
        'id': forms.CharField(max_length=100),
        'name': forms.CharField(max_length=100),
        'category': forms.CharField(max_length=100, required=False),
        'enable': forms.BooleanField(required=False),
        'needVerify': forms.BooleanField(required=False),
    })
    def post(self, request, id, name, category='', enable=True, needVerify=True, **kwargs):
        if CMSFunction.objects.filter(id=id).count() > 0:
            return JsonResponse({
                'code': 1,
                'msg': 'id 为 {} 的功能已存在'.format(id)
            })
        CMSFunction.objects.create(id=id, name=name, category=category, enable=enable, needVerify=needVerify)
        return JsonResponse({
            'code': 0
        })


class FunctionDetail(View):

    @cms_auth
    @cms_permission('functionDetail')
    @validate_args({
        'function_id': forms.CharField(max_length=100),
    })
    @fetch_object(CMSFunction.objects, 'function')
    def get(self, request, function, **kwargs):
        result = {
            'id': function.id,
            'name': function.name,
            'enable': function.enable,
            'needVerity': function.needVerify,
            'category': function.category
        }
        return JsonResponse({
            'code': 0,
            'data': result
        })
