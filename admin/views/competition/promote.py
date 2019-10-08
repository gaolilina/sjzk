from django import forms

from main.models import Competition, CompetitionTeamParticipator
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import fetch_object, validate_args


class CompetitionTeamFinal(BaseView):
    @cms_auth
    @validate_args({
        'team_id': forms.CharField(),
    })
    @fetch_object(Competition.enabled, 'competition')
    def post(self, request, competition, team_id):
        teams = team_id.split(',')
        for t in teams:
            CompetitionTeamParticipator.objects.filter(competition=competition, team_id=int(t)).update(final=True)
        return self.success()
