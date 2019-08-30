from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Activity
from main.utils import abort, get_score_stage
from main.views.like import LikedEntity
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class FollowedActivityList(View):
    ORDERS = ['time_created', '-time_created', 'name', '-name']

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注活动列表

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
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
        """
        c = request.user.followed_activities.count()
        qs = request.user.followed_activities.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.get_current_state(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedActivity(View):
    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def get(self, request, activity):
        """判断当前用户是否关注了activity"""

        if request.user.followed_activities.filter(
                followed=activity).exists():
            abort(200)
        abort(404, '未关注该活动')

    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def post(self, request, activity):
        """令当前用户关注activity"""

        if request.user.followed_activities.filter(
                followed=activity).exists():
            abort(403, '已经关注过该活动')
        request.user.followed_activities.create(followed=activity)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        request.user.save()
        abort(200)

    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def delete(self, request, activity):
        """令当前用户取消关注activity"""

        qs = request.user.followed_activities.filter(followed=activity)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            qs.delete()
            abort(200)
        abort(403, '未关注过该活动')


class LikedActivity(LikedEntity):
    @fetch_object(Activity.enabled, 'activity')
    def get(self, request, activity):
        return super().get(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    def post(self, request, activity):
        return super().post(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    def delete(self, request, activity):
        return super().delete(request, activity)


class ActivityList(View):
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
        l = [{'id': a.activity.id,
              'name': a.activity.name,
              'liker_count': a.activity.likers.count(),
              'time_started': a.activity.time_started,
              'time_ended': a.activity.time_ended,
              'deadline': a.activity.deadline,
              'user_participator_count': a.activity.user_participators.count(),
              'time_created': a.activity.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})