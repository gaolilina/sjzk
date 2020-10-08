from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View
from util.base.view import BaseView

import json

from main.models.activity import *
from admin.models.activity_owner import *

from admin.utils.decorators import *
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args


class AdminActivityAdd(BaseView):
    @admin_auth
    @require_role('xyz')
    def get(self, request):
        context = Context({'user': request.user})
        return self.success(data=context)

    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'name': forms.CharField(max_length=50),
        'tags': forms.CharField(max_length=50),
        'field': forms.CharField(max_length=50),
        'content': forms.CharField(max_length=1000),
        'time_started': forms.DateTimeField(),
        'time_ended': forms.DateTimeField(),
        'allow_user': forms.IntegerField(),
        'status': forms.IntegerField(),
        'type': forms.IntegerField(),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(),
        'stages': forms.CharField(),
    })
    def post(self, request, **kwargs):
        user = request.user
        if kwargs['type'] not in Activity.TYPES:
            return HttpResponseForbidden()

        activity = Activity()

        for k in kwargs:
            if k != "stages":
                setattr(activity, k, kwargs[k])
        activity.save()

        actv_user = ActivityOwner.objects.create(activity=activity, user=user)
        actv_user.save()

        stages = json.loads(kwargs['stages'])
        for st in stages:
            activity.stages.create(status=int(st['status']), time_started=st['time_started'],
                                   time_ended=st['time_ended'])

        context = Context({'msg': '保存成功', 'user': request.user})
        return self.success(data=context)


class AdminActivityEdit(BaseView):
    @fetch_record(Activity.enabled, 'model', 'id')
    @admin_auth
    @require_role('xyz')
    def get(self, request, model):
        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        context = Context(
            {'model': model, 'user': request.user, 'stages': ActivityStage.objects.filter(activity=model)})
        return self.success(data=context)

    @fetch_record(Activity.enabled, 'model', 'id')
    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'name': forms.CharField(max_length=50, required=False),
        'tags': forms.CharField(max_length=50, required=False),
        'field': forms.CharField(max_length=50, required=False),
        'content': forms.CharField(max_length=1000, required=False),
        'deadline': forms.DateTimeField(required=False),
        'time_started': forms.DateTimeField(required=False),
        'time_ended': forms.DateTimeField(required=False),
        'allow_user': forms.IntegerField(),
        'type': forms.IntegerField(required=False),
        'status': forms.IntegerField(required=False),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(required=False),
        'stages': forms.CharField(required=False),
        'achievement': forms.CharField(required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]
        if model.state == Activity.STATE_PASSED \
                or len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0 \
                or 'type' in kwargs and kwargs['type'] not in Activity.TYPES:
            return HttpResponseForbidden()

        for k in kwargs:
            if k != "stages":
                setattr(model, k, kwargs[k])
        # 如果已被拒绝，则重新填写资料会被放入审核中状态
        if model.state == Activity.STATE_NO:
            model.state = Activity.STATE_CHECKING
        model.save()

        if 'stages' in kwargs and kwargs['stages'] != "":
            ActivityStage.objects.filter(activity=model).delete()

            stages = json.loads(kwargs['stages'])
            for st in stages:
                model.stages.create(status=int(st['status']), time_started=st['time_started'],
                                    time_ended=st['time_ended'])

        context = Context({'model': model, 'msg': '保存成功', 'user': request.user,
                           'stages': ActivityStage.objects.filter(activity=model)})
        return self.success(data=context)


class AdminActivityList(BaseView):
    @admin_auth
    @require_role('bxyz')
    def get(self, request):
        try:
            context = Context({'list': ActivityOwner.objects.filter(user=request.user), 'user': request.user})
        except ActivityOwner.DoesNotExist:
            context = Context()
        return self.success(data=context)


class AdminActivityView(BaseView):
    @fetch_record(Activity.enabled, 'model', 'id')
    @admin_auth
    @require_role('bxyz')
    def get(self, request, model):
        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        context = Context(
            {'model': model, 'user': request.user, 'stages': ActivityStage.objects.filter(activity=model)})
        return self.success(data=context)


class AdminActivityExcelView(BaseView):
    @fetch_record(Activity.enabled, 'model', 'id')
    @admin_auth
    @require_role('bxyz')
    def get(self, request, model):
        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        context = Context({'model': model})
        # return HttpResponse(template.render(context),
        #                     content_type="text/csv")
        return self.success(data=context)
