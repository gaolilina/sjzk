from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args
from main.models.activity import *
from admin.models.activity_owner import *

from admin.utils.decorators import *

class AdminActivityAdd(View):
    @require_cookie
    def get(self, request):
        template = loader.get_template("admin_activity/add.html")
        context = Context()
        return HttpResponse(template.render(context))

    @require_cookie
    @validate_args({
        'name': forms.CharField(max_length=50),
        'content': forms.CharField(max_length=1000),
        'deadline': forms.DateTimeField(),
        'time_started': forms.DateTimeField(),
        'time_ended': forms.DateTimeField(),
        'allow_user': forms.BooleanField(),
        'allow_team': forms.BooleanField(),
    })
    def post(self, request, **kwargs):
        user = request.user
        activity = Activity()
        for k in kwargs:
            setattr(activity, k, kwargs[k])
        activity.owner.create(user=user)
        activity.stages.create()
        activity.save()

        template = loader.get_template("admin_activity/add.html")
        context = Context({'msg': '保存成功'})
        return HttpResponse(template.render(context))

class AdminActivityView(View):
    @fetch_record(Activity.enabled, 'model', 'id')
    @require_cookie
    def get(self, request):
        template = loader.get_template("admin_activity/view.html")
        context = Context({'model': model})
        return HttpResponse(template.render(context))

    @fetch_record(Activity.enabled, 'model', 'id')
    @require_cookie
    @validate_args({
        'name': forms.CharField(max_length=50, required=False),
        'content': forms.CharField(max_length=1000, required=False),
        'deadline': forms.DateTimeField(required=False),
        'time_started': forms.DateTimeField(required=False),
        'time_ended': forms.DateTimeField(required=False),
        'allow_user': forms.BooleanField(required=False),
        'allow_team': forms.BooleanField(required=False),
        'stage_status': forms.IntegerField(required=False),
        'stage_province': forms.CharField(max_length=20, required=False),
        'stage_city': forms.CharField(max_length=20, required=False),
        'stage_school': forms.CharField(max_length=20, required=False),
        'stage_user_type': forms.IntegerField(required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        for k in kwargs:
            if k.startswith("stage_"):
                setattr(model.stages, k[6:len(k)], kwargs[k])
            else:
                setattr(model, k, kwargs[k])
        model.save()

        template = loader.get_template("admin_activity/view.html")
        context = Context({'model': model, 'msg': '保存成功'})
        return HttpResponse(template.render(context))

class AdminActivityList(View):
    @require_cookie
    def get(self, request):
        try:
            template = loader.get_template("admin_activity/list.html")
            context = Context({'list': ActivityOwner.objects.get(user=request.user)})
            return HttpResponse(template.render(context))
        except ActivityOwner.DoesNotExist:
            template = loader.get_template("admin_activity/add.html")
            context = Context()
            return HttpResponse(template.render(context))
