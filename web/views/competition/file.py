from django import forms

from main.models import Competition, Team, CompetitionTeamParticipator, CompetitionFile
from main.utils import save_uploaded_file
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class ExpertRateFile(BaseView):

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


class TeamFile(BaseView):

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
        if competition.status in [0, 1, 6]:
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
