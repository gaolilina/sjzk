from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import fetch_record
from main.models import Competition, User, CompetitionTeamParticipator, CompetitionFile, Team
from util.base.view import BaseView
from util.decorator.auth import admin_auth, cms_auth
from util.decorator.param import fetch_object, validate_args


class CompetitionAddExpert(View):
    @admin_auth
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition):
        template = loader.get_template("admin_competition/add_expert.html")
        context = Context({
            'model': competition,
            'user': request.user,
            'experts': competition.experts.all(),
            'all_experts': User.enabled.filter(role='专家').all(),
            'participators': competition.team_participators.all(),
        })
        return HttpResponse(template.render(context))


class CompetitionExpertList(BaseView):

    @cms_auth
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition):
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
        return self.success({'count': c, 'list': l})

    @cms_auth
    @validate_args({
        'expert_id': forms.IntegerField(),
        'competition_id': forms.IntegerField(),
    })
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(User.enabled, 'expert')
    def post(self, request, competition, expert, **kwargs):
        competition.experts.add(expert)
        return self.success()


class TeamExpert(BaseView):
    @admin_auth
    @fetch_record(Competition.enabled, 'model', 'id')
    def get(self, request, model, status):
        template = loader.get_template("admin_competition/file.html")
        context = Context({
            'model': model, 'user': request.user,
            'files': [{
                'team': file.team,
                'file': file.file,
                'id': file.id,
                'time_created': file.time_created,
                'participator': CompetitionTeamParticipator.objects.filter(competition=model,
                                                                           team=file.team).get(),
                'type': file.type,
                'score': file.score,
                'comment': file.comment,
            } for file in CompetitionFile.objects.filter(competition=model, status=status)],
            'teams': CompetitionTeamParticipator.objects.filter(competition=model, final=False).all()
        })
        return HttpResponse(template.render(context))

    @cms_auth
    @validate_args({
        'expert_id': forms.IntegerField(),
        'team_id': forms.IntegerField(),
    })
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'expert')
    def post(self, request, competition, team, expert, **kwargs):
        CompetitionTeamParticipator.objects.filter(
            competition=competition,
            team=team,
        ).update(rater=expert)
        return self.success()
