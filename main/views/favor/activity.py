from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Activity
from main.views.favor import FavoredEntity

from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class FavoredActivityList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    }
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """获取活动收藏列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 收藏时间升序
            1: 收藏时间降序（默认值）
        :return:
            count: 收藏总数
            list: 收藏列表
                id: 活动ID
                name: 活动名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
                province:
        """
        c = request.user.favored_activities.count()
        qs = request.user.favored_activities.order_by(self.ORDERS[order])[offset:offset + limit]

        l = [{'id': a.favored.id,
              'name': a.favored.name,
              'liker_count': a.favored.likers.count(),
              'status': a.favored.status,
              'time_started': a.favored.time_started,
              'time_ended': a.favored.time_ended,
              'deadline': a.favored.deadline,
              'user_participator_count': a.favored.user_participators.count(),
              'time_created': a.favored.time_created,
              'province': a.favored.province} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class FavoredActivity(FavoredEntity):
    @fetch_object(Activity.objects, 'activity')
    def get(self, request, activity):
        return super().get(request, activity)

    @fetch_object(Activity.objects, 'activity')
    def post(self, request, activity):
        return super().post(request, activity)

    @fetch_object(Activity.objects, 'activity')
    def delete(self, request, activity):
        return super().delete(request, activity)