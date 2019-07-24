from django import forms

from modellib.models import CMSFunction
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class AllFunctionList(BaseView):

    @cms_auth
    @cms_permission('allFunctionList')
    @validate_args({
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
    })
    def get(self, request, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        qs = CMSFunction.objects
        total_count = qs.count()
        functions = qs.all()[page * limit:(page + 1) + limit]
        result = {
            'totalCount': total_count,
            'list': [{
                'id': f.id,
                'name': f.name,
                'enable': f.enable,
                'needVerity': f.needVerify,
                'category': f.category
            } for f in functions]
        }
        return self.success(result)

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
            return self.fail(1, 'id 为 {} 的功能已存在'.format(id))
        CMSFunction.objects.create(id=id, name=name, category=category, enable=enable, needVerify=needVerify)
        return self.success()


class FunctionDetail(BaseView):

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
        return self.success(result)
