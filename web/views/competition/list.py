import datetime

from django import forms

from main.models import CompetitionTeamParticipator
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import client_auth
from util.decorator.param import validate_args


class MyJoinedCompetition(BaseView):

    @client_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'history': forms.BooleanField(required=False),
    })
    def get(self, request, page=0, limit=CONSTANT_DEFAULT_LIMIT, history=None, **kwargs):
        """
        我参加的竞赛
        """
        condition = {
            'team__in': request.user.owned_teams.all(),
        }
        # 一般情况只显示未结束的活动
        # true
        if not history:
            condition['competition__time_ended__gt'] = datetime.datetime.now()
            condition['competition__status__in'] = [0, 1, 2, 3, 4, 5]
            # 只展示仍在比赛中的
            condition['final'] = False

        qs = CompetitionTeamParticipator.objects.filter(**condition)
        c = qs.count()
        l = [{
            'id': a.competition.id,
            'name': a.competition.name,
            'liker_count': a.competition.likers.count(),
            'time_started': a.competition.time_started,
            'time_ended': a.competition.time_ended,
            'team_participator_count': a.competition.team_participators.count(),
            'time_created': a.competition.time_created,
            'status': a.competition.status,
            'field': a.competition.field,
            'province': a.competition.province,
        } for a in qs[page * limit:(page + 1) * limit]]
        return self.success({'count': c, 'list': l})
