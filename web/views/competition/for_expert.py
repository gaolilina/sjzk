import datetime

from django import forms

from main.models import Competition, CompetitionFile, CompetitionStage, CompetitionTeamParticipator
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object
from web.views.competition import handle_competition_queryset, competition_to_json


class RatingFileListInCompetition(BaseView):

    @client_auth
    @validate_args({
        'competition_id': forms.IntegerField(),
        'page': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False),
    })
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        # 我评分的团队
        teams = [p.team
                 for p in request.user.rated_team_participators.filter(competition=competition, final=False)]
        qs = CompetitionFile.objects.filter(competition=competition, team__in=teams, status=competition.status)
        return self.success({
            'totalCount': qs.count(),
            'list': [{
                'url': f.file,
                'file_id': f.id,
                'score': f.score,
                'comment': f.comment,
                'type': f.type,
            } for f in qs[limit * page:(page + 1) * limit]]
        })


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
