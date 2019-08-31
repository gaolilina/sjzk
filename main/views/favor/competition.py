from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Competition
from main.views.favor import IFavorSomething

from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class FavoredCompetitionList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    }
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """获取竞赛收藏列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 收藏时间升序
            1: 收藏时间降序（默认值）
        :return:
            count: 收藏总数
            list: 收藏列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
                province:
        """
        c = request.user.favored_competitions.count()
        qs = request.user.favored_competitions.order_by(self.ORDERS[order])[offset:offset + limit]

        l = [{'id': a.favored.id,
              'name': a.favored.name,
              'liker_count': a.favored.likers.count(),
              'status': a.favored.status,
              'time_started': a.favored.time_started,
              'time_ended': a.favored.time_ended,
              'deadline': a.favored.deadline,
              'team_participator_count': a.favored.team_participators.count(),
              'time_created': a.favored.time_created,
              'province': a.favored.province} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class FavoredCompetition(IFavorSomething):
    @fetch_object(Competition.objects, 'competition')
    def get(self, request, competition):
        return super().get(request, competition)

    @fetch_object(Competition.objects, 'competition')
    def post(self, request, competition):
        return super().post(request, competition)

    @fetch_object(Competition.objects, 'competition')
    def delete(self, request, competition):
        return super().delete(request, competition)