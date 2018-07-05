from django import forms
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.template import loader, Context
from django.views.generic import View
import json

from main.utils.decorators import *
from main.models.competition import *
from main.models.team import *
from main.models.user import *
from admin.models.competition_owner import *
from admin.models.admin_user import AdminUser

from admin.utils.decorators import *
from main.utils import *

class AdminCompetitionAdd(View):
    @require_cookie
    @require_role('xyz')
    def get(self, request):
        template = loader.get_template("admin_competition/add.html")
        context = Context({'user': request.user, 'owners': AdminUser.objects.filter(role__contains='a').all()})
        return HttpResponse(template.render(context))

    @require_cookie
    @require_role('xyz')
    @validate_args2({
        'name': forms.CharField(max_length=50),
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
        for k in kwargs:
            if k == 'owner':
                CompetitionOwner.objects.create(competition=competition, user=AdminUser.objects.filter(pk=kwargs['owner']).get())
            elif k != "stages":
                setattr(competition, k, kwargs[k])
        competition.save()

        stages = json.loads(kwargs['stages'])
        for st in stages:
            competition.stages.create(status=int(st['status']), time_started=st['time_started'], time_ended=st['time_ended'])

        template = loader.get_template("admin_competition/add.html")
        context = Context({'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class AdminCompetitionEdit(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('xyz')
    def get(self, request, model):
        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        template = loader.get_template("admin_competition/edit.html")
        context = Context({
            'model': model,
            'user': request.user,
            'stages': CompetitionStage.objects.filter(competition=model),
            'owners': AdminUser.objects.filter(role__contains='a').all(),
        })
        return HttpResponse(template.render(context))

    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('xyz')
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
        'stages': forms.CharField(required=False),
        'owner': forms.IntegerField(required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]

        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        for k in kwargs:
            if k == 'owner':
                CompetitionOwner.objects.filter(competition=competition).update(user=AdminUser.objects.filter(pk=kwargs['owner']).get())
            elif k != "stages":
                setattr(model, k, kwargs[k])
        model.save()
        
        if 'stages' in kwargs and kwargs['stages'] != "":
            CompetitionStage.objects.filter(competition=model).delete()

            stages = json.loads(kwargs['stages'])
            for st in stages:
                model.stages.create(status=int(st['status']), time_started=st['time_started'], time_ended=st['time_ended'])

        template = loader.get_template("admin_competition/edit.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user, 'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))

class AdminCompetitionList(View):
    @require_cookie
    @require_role('axyz')
    def get(self, request):
        try:
            template = loader.get_template("admin_competition/list.html")
            context = Context({'list': CompetitionOwner.objects.filter(user=request.user), 'user': request.user})
            return HttpResponse(template.render(context))
        except CompetitionOwner.DoesNotExist:
            template = loader.get_template("admin_competition/add.html")
            context = Context({'user': request.user})
            return HttpResponse(template.render(context))

class AdminCompetitionView(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('axyz')
    def get(self, request, model):
        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()
            
        template = loader.get_template("admin_competition/view.html")
        context = Context({'model': model, 'user': request.user, 'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))

class AdminCompetitionFilesView(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('axyz')
    def get(self, request, model, status):
        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        template = loader.get_template("admin_competition/file.html")
        context = Context({'model': model, 'user': request.user,
            'files': [{
                'team': file.team,
                'file': file.file,
                'id': file.id,
                'time_created': file.time_created,
                'participator': CompetitionTeamParticipator.objects.filter(competition=model, team=file.team).get(),
                'type': file.type,
                'score': file.score,
                'comment': file.comment,
            } for file in CompetitionFile.objects.filter(competition=model, status=status)]})
        return HttpResponse(template.render(context))

class AdminCompetitionExcelView(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('axyz')
    def get(self, request, model):
        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        template = loader.get_template("admin_competition/excel.html")
        context = Context({'model': model})
        return HttpResponse(template.render(context),
            content_type="text/csv")

class AdminCompetitionAwardEdit(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('axyz')
    def get(self, request, model):
        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()

        template = loader.get_template("admin_competition/award.html")
        context = Context({'model': model, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(Competition.enabled, 'model', 'id')
    @require_cookie
    @require_role('axyz')
    @validate_args2({
        'awards': forms.CharField(),
    })
    def post(self, request, **kwargs):
        user = request.user
        model = kwargs["model"]

        if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
            return HttpResponseForbidden()
        
        awards = json.loads(kwargs['awards'])
        for a in awards:
            for id in awards[a]:
                model.awards.create(award=a, team=Team.objects.filter(id=int(id))[0])

        template = loader.get_template("admin_competition/award.html")
        context = Context({'model': model, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class CompetitionFileExpert(View):
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    @require_cookie
    @validate_args({
        'expert_id': forms.IntegerField(),
    })
    def post(self, request, competition, team, expert_id):
        expert = User.objects.filter(pk=expert_id).get()
        CompetitionTeamParticipator.objects.filter(
            competition=competition,
            team=team,
        ).update(rater=expert)
        abort(200)

class CompetitionExpertList(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_cookie
    @validate_args({
        'api': forms.IntegerField(required=False),
    })
    def get(self, request, competition, api=0):
        if api == 1:
            c = competition.experts.all().count()
            qs = competition.experts.all()
            l = [{'id': user.id,
                'time_created': user.time_created,
                'name': user.name,
                'icon_url': user.icon,
                'description': user.description,
                'email': user.email,
                'gender': user.gender,
                'birthday': user.birthday,
                'province': user.province,
                'city': user.city,
                'county': user.county,
                'follower_count': user.followers.count(),
                'followed_count': user.followed_users.count() + user.followed_teams.count(),
                'friend_count': user.friends.count(),
                'liker_count': user.likers.count(),
                'visitor_count': user.visitors.count(),
                'is_verified': user.is_verified,
                'is_role_verified': user.is_role_verified,
                'role': user.role,
                'adept_field': user.adept_field,
                'adept_skill': user.adept_skill,
                'expect_role': user.expect_role,
                'follow_field': user.follow_field,
                'follow_skill': user.follow_skill,
                'unit1': user.unit1,
                'unit2': user.unit2,
                'profession': user.profession,
                'score': user.score} for user in qs]
            return JsonResponse({'count': c, 'list': l})
        template = loader.get_template("admin_competition/add_expert.html")
        context = Context({
            'model': competition,
            'user': request.user,
            'experts': competition.experts.all(),
            'all_experts': User.enabled.filter(role='专家').all(),
            'participators': competition.team_participators.all(),
        })
        return HttpResponse(template.render(context))
    
    @fetch_object(Competition.enabled, 'competition')
    @require_cookie
    @validate_args({
        'expert_id': forms.IntegerField(),
    })
    def post(self, request, competition, expert_id):
        expert = User.objects.filter(pk=expert_id).get()
        competition.experts.add(expert)
        abort(200)