import datetime

from django import forms
from django.db.models import Count

from main.models import CompetitionTeamParticipator, CompetitionStage
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import client_auth
from util.decorator.param import validate_args


class MyJoinedCompetition(BaseView):

    @client_auth
    @validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
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
            condition['competition__status__lt'] = CompetitionStage.STAGE_END
            # 只展示仍在比赛中的
            condition['final'] = False

        qs = handle_competition_queryset(CompetitionTeamParticipator.objects.filter(**condition))
        c = qs.count()
        l = [competition_to_json(a) for a in qs[page * limit:(page + 1) * limit]]
        return self.success({'count': c, 'list': l})


class MyRatingCompetition(BaseView):

    @client_auth
    @validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        """
        我评分的竞赛
        """
        # 只显示未结束的活动
        condition = {
            'rater': request.user,
            'competition__time_ended__gt': datetime.datetime.now(),
            'competition__status__lt': CompetitionStage.STAGE_END,
            'final': False,
        }
        qs = handle_competition_queryset(CompetitionTeamParticipator.objects.filter(**condition))
        c = qs.count()
        l = [competition_to_json(a) for a in qs[page * limit:(page + 1) * limit]]
        return self.success({'count': c, 'list': l})


def handle_competition_queryset(qs):
    return qs.values(
        'competition_id',
        'competition__name',
        'competition__time_started',
        'competition__time_ended',
        'competition__time_created',
        'competition__status',
        'competition__field',
        'competition__province',
    ).annotate(Count('competition_id'))


def competition_to_json(competition):
    return {
        'id': competition['competition_id'],
        'name': competition['competition__name'],
        'time_started': competition['competition__time_started'],
        'time_ended': competition['competition__time_ended'],
        'time_created': competition['competition__time_created'],
        'status': competition['competition__status'],
        'field': competition['competition__field'],
        'province': competition['competition__province'],
    }
