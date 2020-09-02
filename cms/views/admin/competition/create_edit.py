import json
from datetime import datetime

from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from admin.models import AdminUser, CompetitionOwner
from admin.utils.decorators import require_role
from main.models import Competition, CompetitionStage
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args, fetch_object
from util.decorator.permission import admin_permission
from util.base.view import BaseView


class AdminCompetitionAdd(BaseView):
    @admin_auth
    def get(self, request):
        context = Context({
            'user': request.user,
            'owners': AdminUser.objects.filter(role__contains='a').all()
        })
        return self.success(data=context)

    @admin_auth
    @admin_permission('create_competition')
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
        dateformat = "%Y-%m-%d %H:%M"

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

        context = Context({'msg': '保存成功', 'user': request.user})
        return self.success(data=context)


class AdminCompetitionEdit(BaseView):
    @admin_auth
    @require_role('xyz')
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition):
        owner = CompetitionOwner.objects.filter(competition=competition).all()
        context = Context({
            'model': competition,
            'user': request.user,
            'stages': CompetitionStage.objects.filter(competition=competition),
            'owners': AdminUser.objects.filter(role__contains='a').all(),
            'ownerid': owner[0].user.id if len(owner) > 0 else -1,
        })
        return self.success(data=context)

    @admin_auth
    @admin_permission('modify_competition')
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
    @fetch_object(Competition.enabled, 'competition')
    def post(self, request, competition, stages=None, **kwargs):

        for k in kwargs:
            if k == 'owner':
                CompetitionOwner.objects.filter(competition=competition).update(
                    user=AdminUser.objects.filter(pk=kwargs['owner']).get())
            else:
                setattr(competition, k, kwargs[k])
        competition.save()

        if stages:
            CompetitionStage.objects.filter(competition=competition).delete()
            stages = json.loads(stages)
            for st in stages:
                competition.stages.create(status=int(st['status']), time_started=st['time_started'],
                                          time_ended=st['time_ended'])

        context = Context({'model': competition, 'msg': '保存成功', 'user': request.user,
                           'stages': CompetitionStage.objects.filter(competition=competition)})
        return self.success(data=context)
