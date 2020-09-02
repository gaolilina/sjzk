from django import forms
from django.http import HttpResponse
from django.template import Context, loader

from main.models import Competition, CompetitionTeamParticipator
from util.base.view import BaseView
from util.decorator.auth import cms_auth, admin_auth
from util.decorator.param import fetch_object, validate_args
from util.decorator.permission import cms_permission


class CompetitionTeamFinal(BaseView):
    @admin_auth
    @validate_args({
        'competition_id': forms.IntegerField(),
        'final': forms.BooleanField(required=False),
    })
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition, final=False):
        template = loader.get_template("admin_competition/promote_team.html")
        c = CompetitionTeamParticipator.objects.filter(competition=competition, final=final).all().count()
        qs = CompetitionTeamParticipator.objects.filter(competition=competition, final=final).all()
        context = Context({
            'teams': qs,
        })
        return HttpResponse(template.render(context))

    @cms_auth
    @cms_permission('eliminate_team_in_competition')
    @validate_args({
        'competition_id': forms.IntegerField(),
        'team_id': forms.CharField(),
    })
    @fetch_object(Competition.enabled, 'competition')
    def post(self, request, competition, team_id):
        teams = team_id.split(',')
        for t in teams:
            CompetitionTeamParticipator.objects.filter(competition=competition, team_id=int(t)).update(final=True)
        return self.success()
