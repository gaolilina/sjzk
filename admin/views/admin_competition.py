from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View
import json

from main.utils.decorators import validate_args
from main.models.competition import *
from admin.models.competition_owner import *

from admin.utils.decorators import *

class AdminCompetitionAdd(View):
    @require_cookie
    def get(self, request):
        template = loader.get_template("admin_competition/add.html")
        context = Context({'user': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @validate_args2({
        'name': forms.CharField(max_length=50),
        'content': forms.CharField(max_length=1000),
        'deadline': forms.DateTimeField(),
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
    })
    def post(self, request, **kwargs):
        user = request.user
        competition = Competition()
        for k in kwargs:
            if k != "stages":
                setattr(competition, k, kwargs[k])
        competition.save()

        comp_user = CompetitionOwner.objects.create(competition=competition, user=user)
        comp_user.save()

        stages = json.loads(kwargs['stages'])
        for st in stages:
            competition.stages.create(status=int(st['status']), time_started=st['time_started'], time_ended=st['time_ended'])

        template = loader.get_template("admin_competition/add.html")
        context = Context({'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class AdminCompetitionEdit(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    def get(self, request, model):
        template = loader.get_template("admin_competition/edit.html")
        context = Context({'model': model, 'user': request.user, 'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))

    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @validate_args2({
        'name': forms.CharField(max_length=50, required=False),
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
        'stages': forms.CharField(),
    })
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]
        for k in kwargs:
            if k != "stages":
                setattr(model, k, kwargs[k])
        model.save()

        CompetitionStage.objects.filter(competition=model).delete()

        stages = json.loads(kwargs['stages'])
        for st in stages:
            model.stages.create(status=int(st['status']), time_started=st['time_started'], time_ended=st['time_ended'])

        template = loader.get_template("admin_competition/edit.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user, 'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))

class AdminCompetitionList(View):
    @require_cookie
    def get(self, request):
        try:
            template = loader.get_template("admin_competition/list.html")
            context = Context({'list': CompetitionOwner.objects.filter(user=request.user), 'user': request.user})
            return HttpResponse(template.render(context))
        except CompetitionOwner.DoesNotExist:
            template = loader.get_template("admin_competition/add.html")
            context = Context()
            return HttpResponse(template.render(context))

class AdminCompetitionView(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    def get(self, request, model):
        template = loader.get_template("admin_competition/view.html")
        context = Context({'model': model, 'user': request.user, 'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))