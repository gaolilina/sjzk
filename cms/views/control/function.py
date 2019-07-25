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
        'category': forms.CharField(max_length=100, required=False),
    })
    def get(self, request, category=None, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        filter_param = {}
        if category is not None:
            filter_param['category'] = category
        qs = CMSFunction.objects.filter(**filter_param)
        total_count = qs.count()
        functions = qs[page * limit:(page + 1) + limit]
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
        'id': forms.CharField(min_length=6, max_length=100),
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


class MyFunctionList(BaseView):
    @cms_auth
    @validate_args({
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
        'category': forms.CharField(max_length=100, required=False),
    })
    def get(self, request, category=None, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        # 获取我的功能列表
        my_role = request.user.system_role
        total_count = 0
        functions = []
        if my_role is not None:
            filter_param = {}
            if category is not None:
                filter_param['category'] = category
            qs = (my_role.functions if my_role.is_admin() else CMSFunction.objects.all()).filter(**filter_param)
            total_count = qs.count()
            functions = qs[page * limit:(page + 1) + limit]
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

    @cms_auth
    @cms_permission('updateFunction')
    @validate_args({
        'function_id': forms.CharField(max_length=100),
        'name': forms.CharField(max_length=100, required=False),
        'category': forms.CharField(max_length=100, required=False),
        'enable': forms.BooleanField(required=False),
        'needVerify': forms.BooleanField(required=False),
    })
    @fetch_object(CMSFunction.objects, 'function')
    def post(self, request, function, **kwargs):
        param_list = []
        update_param = {}
        for p in param_list:
            if p in kwargs:
                update_param[p] = kwargs[p]
        if len(update_param) > 0:
            CMSFunction.objects.filter(id=function.id).update(**update_param)
        return self.success()
