import json

from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import require_role, fetch_record
from main.models import Activity, ActivityStage
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args


class ActivityView(View):
    @admin_auth
    @require_role('yz')
    @fetch_record(Activity.objects, 'mod', 'id')
    def get(self, request, mod):
        template = loader.get_template("activity/activity.html")
        context = Context({'model': mod, 'user': request.user, 'stages': ActivityStage.objects.filter(activity=mod)})
        return HttpResponse(template.render(context))

    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'name': forms.CharField(max_length=50, required=False),
        'tags': forms.CharField(max_length=50, required=False),
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
    @fetch_record(Activity.enabled, 'model', 'id')
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]
        if model.state == Activity.STATE_PASSED \
                or 'type' in kwargs and kwargs['type'] not in Activity.TYPES:
            return HttpResponseForbidden()

        for k in kwargs:
            if k != "stages":
                setattr(model, k, kwargs[k])
        model.save()

        if 'stages' in kwargs and kwargs['stages'] != "":
            ActivityStage.objects.filter(activity=model).delete()

            stages = json.loads(kwargs['stages'])
            for st in stages:
                model.stages.create(status=int(st['status']), time_started=st['time_started'],
                                    time_ended=st['time_ended'])

        template = loader.get_template("activity/activity.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user,
                           'stages': ActivityStage.objects.filter(activity=model)})
        return HttpResponse(template.render(context))


class ActivityList(View):
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = Activity.objects.filter(activity_id=kwargs["id"])
            template = loader.get_template("activity/activity_list.html")
            context = Context({'page': page, 'list': list, 'redir': 'admin:activity:activity', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("activity/index.html")
            if Activity == Activity:
                redir = 'admin:activity:activity'
            else:
                redir = 'admin:activity:activity_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Activity.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'activity', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("activity/index.html")
            context = Context({'rb': 'activity', 'user': request.user})
            return HttpResponse(template.render(context))