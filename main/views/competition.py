from django import forms
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import View

from ChuangYi.settings import UPLOADED_URL
from ..models import Competition, Team
from ..utils import abort
from ..utils.decorators import *


__all__ = ['List', 'Detail', 'TeamParticipatorList']


class List(View):
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取活动列表"""

        c = Competition.enabled.count()
        qs = Competition.enabled.all()[offset: offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class Detail(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    def get(self, request, competition):
        """获取活动详情"""

        return JsonResponse({
            'id': competition.id,
            'name': competition.name,
            'content': competition.content,
            'time_started': competition.time_started,
            'time_ended': competition.time_ended,
            'deadline': competition.deadline,
            'allow_user': competition.allow_user,
            'allow_team': competition.allow_team,
            'team_participator_count': competition.team_participators.count(),
            'time_created': competition.time_created,
        })


class TeamParticipatorList(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        """获取报名团队列表"""

        c = competition.team_participators.count()
        qs = competition.team_participators.all()[offset: offset + limit]
        l = [{'id': p.team.id,
              'name': p.team.name,
              'icon_url': p.team.icon} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Competition.enabled, 'competition')
    @validate_args({'team_id': forms.IntegerField()})
    @require_token
    def post(self, request, competition, team_id):
        """报名"""

        if not competition.allow_team:
            abort(403)

        try:
            team = Team.enabled.get(id=team_id)
        except Team.DoesNotExist:
            abort(400)
        else:
            if not competition.team_participators.filter(team=team).exists():
                competition.team_participators.create(team=team)
            abort(200)
