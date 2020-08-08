from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Competition
from main.utils import abort, get_score_stage
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class FollowedCompetitionList(View):
    ORDERS = ['time_created', '-time_created', 'name', '-name']

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注竞赛列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
        """
        c = request.user.followed_competitions.count()
        qs = request.user.followed_competitions.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.status,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class FollowedCompetition(View):
    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def get(self, request, competition):
        """判断当前用户是否关注了competition"""

        if request.user.followed_competitions.filter(
                followed=competition).exists():
            abort(200)
        abort(403, '未关注该竞赛')

    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def post(self, request, competition):
        """令当前用户关注competition"""

        if request.user.followed_competitions.filter(
                followed=competition).exists():
            abort(403, '已经关注过该竞赛')
        request.user.followed_competitions.create(followed=competition)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        request.user.save()
        abort(200)

    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def delete(self, request, competition):
        """令当前用户取消关注competition"""

        qs = request.user.followed_competitions.filter(followed=competition)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            qs.delete()
            abort(200)
        abort(403, '未关注过该竞赛')