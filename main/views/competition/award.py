from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Competition
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class CompetitionAwardList(View):
    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        """获取竞赛的评比列表
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 评比总数
            list: 评比列表
                id: 评比ID
                team_id: 团队ID
                team_name: 团队名称
                icon: 团队头像
                award: 获奖情况
                time_created: 创建时间
        """

        c = competition.awards.count()
        qs = competition.awards.all()[offset: offset + limit]
        l = [{
            'id': p.id,
            'team_id': p.team.id,
            'team_name': p.team.name,
            'icon': p.team.icon,
            'award': p.award,
            'time_created': p.time_created
        } for p in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})