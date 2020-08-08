from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team
from main.utils import abort, get_score_stage
from main.views.follow import SomethingFollower
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class FollowedTeamList(View):
    ORDERS = [
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注团队列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 团队名称升序
            3: 团队名称降序
        :return:
            count: 关注的团队总数
            list: 关注的用户列表
                id: 团队ID
                name: 团队昵称
                icon_url: 团队头像
                time_created: 关注时间
        """
        c = request.user.followed_teams.count()
        qs = request.user.followed_teams.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'name': r.followed.name,
              'icon_url': r.followed.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class FollowedTeam(View):
    @app_auth
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        """判断当前用户是否关注了team"""

        if request.user.followed_teams.filter(followed=team).exists():
            abort(200)
        abort(403, '未关注该团队')

    @app_auth
    @fetch_object(Team.enabled, 'team')
    def post(self, request, team):
        """令当前用户关注team"""

        if request.user.followed_teams.filter(followed=team).exists():
            abort(403, '已经关注过该团队')
        request.user.followed_teams.create(followed=team)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="增加一个关注")
        request.user.save()
        team.save()
        abort(200)

    @app_auth
    @fetch_object(Team.enabled, 'team')
    def delete(self, request, team):
        """令当前用户取消关注team"""

        qs = request.user.followed_teams.filter(followed=team)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            team.score -= get_score_stage(1)
            team.score_records.create(
                score=-get_score_stage(1), type="受欢迎度",
                description="取消关注")
            request.user.save()
            team.save()
            qs.delete()
            abort(200)
        abort(403, '未关注过该团队')


class TeamFollowerList(SomethingFollower):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    def get(self, request, team):
        return super().get(request, team)