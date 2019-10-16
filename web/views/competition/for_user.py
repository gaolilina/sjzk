import datetime

from django import forms

from main.models import CompetitionTeamParticipator, CompetitionStage, Competition, Team, CompetitionFile
from main.utils import save_uploaded_file
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object
from web.views.competition import handle_competition_queryset, competition_to_json


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


class UploadFileForTeamInCompetition(BaseView):

    @client_auth
    @validate_args({
        'competition_id': forms.IntegerField(),
        'team_id': forms.IntegerField(),
        'type': forms.IntegerField(),
        'file': forms.FileField(),
    })
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    def post(self, request, competition, team, file, type, **kwargs):
        if competition.status in CompetitionStage.STAGES_ERROR:
            return self.fail(4, '当前阶段不能上传文件')
        if request.user != team.owner:
            return self.fail(1, '队长操作')
        part = CompetitionTeamParticipator.objects.filter(team=team, competition=competition)
        if not part.exists():
            return self.fail(2, '未参加竞赛')
        if part.first().final:
            return self.fail(5, '未能到达当前阶段')
        filename = save_uploaded_file(file, competition.id, competition.status, team.id)
        if not filename:
            return self.fail(3, '上传文件失败')
        f = CompetitionFile.objects.filter(team=team, competition=competition, status=competition.status, type=type)
        # 如果上传过直接覆盖
        if f.exists():
            f.update(file=filename)
        else:
            competition.team_files.create(team=team, status=competition.status, type=type, file=filename)
        return self.success()
