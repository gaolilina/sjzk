from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

import json

from main.utils.decorators import validate_args
from main.models.activity import *
from admin.models.activity_owner import *

from admin.utils.decorators import *

class AdminActivityAdd(View):
    @require_cookie
    @require_role('xyz')
    def get(self, request):
        template = loader.get_template("admin_activity/add.html")
        context = Context({'user': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @require_role('xyz')
    @validate_args2({
        'name': forms.CharField(max_length=50),
        'content': forms.CharField(max_length=1000),
        'deadline': forms.DateTimeField(),
        'time_started': forms.DateTimeField(),
        'time_ended': forms.DateTimeField(),
        'allow_user': forms.IntegerField(),
        'status': forms.IntegerField(),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(),
        'stages': forms.CharField(),
    })
    def post(self, request, **kwargs):
        user = request.user
        activity = Activity()
        
        for k in kwargs:
            if k != "stages":
                setattr(activity, k, kwargs[k])
        activity.save()

        actv_user = ActivityOwner.objects.create(activity=activity, user=user)
        actv_user.save()
        
        stages = json.loads(kwargs['stages'])
        for st in stages:
            activity.stages.create(status=int(st['status']), time_started=st['time_started'], time_ended=st['time_ended'])

        template = loader.get_template("admin_activity/add.html")
        context = Context({'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class AdminActivityEdit(View):
    @fetch_record(Activity.enabled, 'model', 'id')
    @require_cookie
    @require_role('xyz')
    def get(self, request, model):
        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()
        
        template = loader.get_template("admin_activity/edit.html")
        context = Context({'model': model, 'user': request.user, 'stages': ActivityStage.objects.filter(activity=model)})
        return HttpResponse(template.render(context))

    @fetch_record(Activity.enabled, 'model', 'id')
    @require_cookie
    @require_role('xyz')
    @validate_args2({
        'name': forms.CharField(max_length=50, required=False),
        'content': forms.CharField(max_length=1000, required=False),
        'deadline': forms.DateTimeField(required=False),
        'time_started': forms.DateTimeField(required=False),
        'time_ended': forms.DateTimeField(required=False),
        'allow_user': forms.IntegerField(),
        'status': forms.IntegerField(required=False),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(required=False),
        'stages': forms.CharField(required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]

        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        for k in kwargs:
            if k != "stages":
                setattr(model, k, kwargs[k])
        model.save()

        if 'stages' in kwargs and kwargs['stages'] != "":
            ActivityStage.objects.filter(activity=model).delete()

            stages = json.loads(kwargs['stages'])
            for st in stages:
                model.stages.create(status=int(st['status']), time_started=st['time_started'], time_ended=st['time_ended'])

        template = loader.get_template("admin_activity/edit.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user, 'stages': ActivityStage.objects.filter(activity=model)})
        return HttpResponse(template.render(context))

class AdminActivityList(View):
    @require_cookie
    @require_role('bxyz')
    def get(self, request):
        try:
            template = loader.get_template("admin_activity/list.html")
            context = Context({'list': ActivityOwner.objects.filter(user=request.user), 'user': request.user})
            return HttpResponse(template.render(context))
        except ActivityOwner.DoesNotExist:
            template = loader.get_template("admin_activity/add.html")
            context = Context()
            return HttpResponse(template.render(context))

class AdminActivityView(View):
    @fetch_record(Activity.enabled, 'model', 'id')
    @require_cookie
    @require_role('bxyz')
    def get(self, request, model):
        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        template = loader.get_template("admin_activity/view.html")
        context = Context({'model': model, 'user': request.user, 'stages': ActivityStage.objects.filter(activity=model)})
        return HttpResponse(template.render(context))

class AdminActivityExcelView(View):
    @fetch_record(Activity.enabled, 'model', 'id')
    @require_cookie
    @require_role('bxyz')
    def get(self, request, model):
        if len(ActivityOwner.objects.filter(activity=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        template = loader.get_template("admin_activity/excel.html")
        context = Context({'model': model})
        return HttpResponse(template.render(context),
            content_type="text/csv")