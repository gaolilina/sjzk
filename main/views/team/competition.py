from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team, CompetitionTeamParticipator
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class CompetitionList(View):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队的竞赛列表"""

        r = CompetitionTeamParticipator.objects.filter(team=team)
        c = r.count()
        qs = r[offset: offset + limit]
        l = [{'id': a.competition.id,
              'name': a.competition.name,
              'time_started': a.competition.time_started,
              'time_ended': a.competition.time_ended,
              'deadline': a.competition.deadline,
              'team_participator_count':
                  a.competition.team_participators.count(),
              'time_created': a.competition.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class TeamAwardList(View):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队参加的竞赛评比列表
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 评比总数
            list: 评比列表
                id: 评比ID
                competition_id: 竞赛ID
                competition_name: 竞赛名称
                award: 获奖情况
                time_created: 创建时间
        """

        c = team.awards.count()
        qs = team.awards.all()[offset: offset + limit]
        l = [{'id': p.id,
              'competition_id': p.competition.id,
              'competition_name': p.competition.name,
              'award': p.award,
              'time_started': p.time_started} for p in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})
