from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Activity
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class Detail(View):
    @app_auth
    @fetch_object(Activity.enabled, 'activity')
    def get(self, request, activity):
        """获取活动详情
        :return:
            id: 活动ID
            name: 活动名
            liker_count: 点赞数
            time_started: 开始时间
            time_ended: 结束时间
            deadline: 截止时间
            allow_user: 允许报名人数
            user_participator_count: 已报名人数
            status: 活动当前阶段
            province: 省
            city: 城市
            unit: 机构
            user_type: 参与人员身份
            time_created: 创建时间
        """

        owner = activity.owner.first()
        return JsonResponse({
            'id': activity.id,
            'name': activity.name,
            'liker_count': activity.likers.count(),
            'content': activity.content,
            'time_started': activity.time_started,
            'time_ended': activity.time_ended,
            'deadline': activity.deadline,
            'allow_user': activity.allow_user,
            'user_participator_count': activity.user_participators.count(),
            'status': activity.get_current_state(),
            'achievement': activity.achievement,
            'province': activity.province,
            'city': activity.city,
            'unit': activity.unit,
            'user_type': activity.user_type,
            'time_created': activity.time_created,
            'owner': owner.user.name if owner is not None else "",
            'owner_id': owner.user.id if owner is not None else -1,
            'owner_user': activity.owner_user.id if activity.owner_user is not None else -1,
            'expense': activity.expense,
            'experts': [{
                'name': ex.name,
                'username': ex.username,
                'id': ex.id
            } for ex in activity.experts.all()],
            'stages': [{
                'status': p.status,
                'time_started': p.time_started,
                'time_ended': p.time_ended,
            } for p in activity.stages.all()]
        })


class ActivityStage(View):
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    @fetch_object(Activity.enabled, 'activity')
    def get(self, request, activity, offset=0, limit=10):
        """获取活动的阶段列表
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 阶段总数
            list: 阶段列表
                id: 阶段ID
                stage: 阶段名称:0:前期宣传, 1:报名, 2:结束
                time_started: 开始时间
                time_ended: 结束时间
                time_created: 创建时间
        """

        c = activity.stages.count()
        qs = activity.stages.all().order_by("status")[offset: offset + limit]
        l = [{'id': p.id,
              'status': p.status,
              'time_started': p.time_started,
              'time_ended': p.time_ended,
              'time_created': p.time_created,
              } for p in qs]
        return JsonResponse({'count': c, 'list': l})
