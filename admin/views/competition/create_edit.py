import json
from datetime import datetime

from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from admin.models import AdminUser, CompetitionOwner
from admin.utils.decorators import require_role, fetch_record
from main.models import Competition, CompetitionStage
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args


class AdminCompetitionAdd(View):
    @admin_auth
    @require_role('xyz')
    def get(self, request):
        template = loader.get_template("admin_competition/add.html")
        context = Context({
            'user': request.user,
            'owners': AdminUser.objects.filter(role__contains='a').all()
        })
        return HttpResponse(template.render(context))

    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'name': forms.CharField(max_length=50),
        'tags': forms.CharField(max_length=50),
        'field': forms.CharField(max_length=50),
        'content': forms.CharField(max_length=1000),
        'deadline': forms.DateTimeField(required=False),
        'time_started': forms.DateTimeField(),
        'time_ended': forms.DateTimeField(),
        'allow_team': forms.IntegerField(),
        'status': forms.IntegerField(),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'min_member': forms.IntegerField(),
        'max_member': forms.IntegerField(),
        'user_type': forms.IntegerField(),
        'stages': forms.CharField(),
        'owner': forms.IntegerField(),
    })
    def post(self, request, **kwargs):
        user = request.user
        competition = Competition()
        dateformat = "%Y-%m-%d"

        if 'stages' in kwargs and kwargs['stages'] != "":
            stages = json.loads(kwargs['stages'])
            for st in stages:
                if datetime.strptime(st['time_started'], dateformat) < kwargs['time_started'] or datetime.strptime(
                        st['time_ended'], dateformat) > kwargs['time_ended']:
                    return HttpResponseForbidden('时间输入有误')

        for k in kwargs:
            if k != "stages":
                setattr(competition, k, kwargs[k])
        competition.save()
        CompetitionOwner.objects.create(competition=competition, user=user)
        stages = json.loads(kwargs['stages'])
        for st in stages:
            competition.stages.create(status=int(st['status']), time_started=st['time_started'],
                                      time_ended=st['time_ended'])

        template = loader.get_template("admin_competition/add.html")
        context = Context({'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class AdminCompetitionEdit(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @admin_auth
    @require_role('xyz')
    def get(self, request, model):
        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        template = loader.get_template("admin_competition/edit.html")
        owner = CompetitionOwner.objects.filter(competition=model).all()
        context = Context({
            'model': model,
            'user': request.user,
            'stages': CompetitionStage.objects.filter(competition=model),
            'owners': AdminUser.objects.filter(role__contains='a').all(),
            'ownerid': owner[0].user.id if len(owner) > 0 else -1,
        })
        return HttpResponse(template.render(context))

    @fetch_record(Competition.enabled, 'model', 'id')
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
        'allow_team': forms.IntegerField(),
        'status': forms.IntegerField(required=False),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'min_member': forms.IntegerField(required=False),
        'max_member': forms.IntegerField(required=False),
        'user_type': forms.IntegerField(required=False),
        'stages': forms.CharField(required=False),
        'owner': forms.IntegerField(required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]
        dateformat = "%Y-%m-%d"

        if 'stages' in kwargs and kwargs['stages'] != "":
            stages = json.loads(kwargs['stages'])
            for st in stages:
                if datetime.strptime(st['time_started'], dateformat) < kwargs['time_started'] or datetime.strptime(
                        st['time_ended'], dateformat) > kwargs['time_ended']:
                    return HttpResponseForbidden('时间输入有误')

        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        for k in kwargs:
            if k == 'owner':
                CompetitionOwner.objects.filter(competition=model).update(
                    user=AdminUser.objects.filter(pk=kwargs['owner']).get())
            elif k != "stages":
                setattr(model, k, kwargs[k])
        model.save()

        if 'stages' in kwargs and kwargs['stages'] != "":
            CompetitionStage.objects.filter(competition=model).delete()

            stages = json.loads(kwargs['stages'])
            for st in stages:
                model.stages.create(status=int(st['status']), time_started=st['time_started'],
                                    time_ended=st['time_ended'])

        template = loader.get_template("admin_competition/edit.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user,
                           'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))