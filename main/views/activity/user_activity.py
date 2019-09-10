from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Activity
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class MyJoinedActivityList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户参加的活动列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 活动总数
            list: 活动列表
                id: 活动ID
                name: 活动名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
        """

        k = self.ORDERS[order]
        c = request.user.activities.count()
        qs = request.user.activities.order_by(k)[offset: offset + limit]
        l = [activity_to_json(a.activity) for a in qs]
        return JsonResponse({'count': c, 'list': l})


class MyCreatedActivityList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'state': forms.IntegerField(required=False),
    })
    def get(self, request, state=None, offset=0, limit=10, order=1):
        filter_param = {
            'owner_user': request.user,
        }
        if state is not None:
            filter_param['state'] = state
        qs = Activity.objects.filter(**filter_param).order_by(self.ORDERS[order])
        c = qs.count()
        l = [activity_to_json(a) for a in qs[offset: offset + limit]]
        return JsonResponse({'count': c, 'list': l})


def activity_to_json(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'liker_count': activity.likers.count(),
        'time_started': activity.time_started,
        'time_ended': activity.time_ended,
        'deadline': activity.deadline,
        'user_participator_count': activity.user_participators.count(),
        'time_created': activity.time_created,
        'state': activity.state,  # 当前状态
    }
