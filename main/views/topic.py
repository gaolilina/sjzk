from django import forms
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from util.decorator.param import validate_args, fetch_object
from ..models import Topic
from ..utils import abort
from ..utils.decorators import *


__all__ = ['List', 'Detail', 'TopicStage', 'UserParticipatorList', 'Search',
           'Screen']


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'history': forms.BooleanField(required=False),
    })
    def get(self, request, offset=0, limit=10, order=1, history=False):
        """获取课题列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
        :param history: 是否往期课题（默认否）
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 课题总数
            list: 课题列表
                id: 课题ID
                name: 课题名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
                province:
        """

        k = self.ORDERS[order]
        if history is False:
            c = Topic.enabled.exclude(status=2).count()
            qs = Topic.enabled.exclude(
                status=2).order_by(k)[offset: offset + limit]
        else:
            c = Topic.enabled.filter(status=2).count()
            qs = Topic.enabled.filter(
                status=2).order_by(k)[offset: offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.status,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'time_created': a.time_created,
              'province': a.province} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class Detail(View):
    @require_token
    @fetch_object(Topic.enabled, 'topic')
    def get(self, request, topic):
        """获取课题详情
        :return:
            id: 课题ID
            name: 课题名
            liker_count: 点赞数
            time_started: 开始时间
            time_ended: 结束时间
            deadline: 截止时间
            allow_user: 允许报名人数
            user_participator_count: 已报名人数
            status: 课题当前阶段
            province: 省
            city: 城市
            unit: 机构
            user_type: 参与人员身份
            time_created: 创建时间
        """

        return JsonResponse({
            'id': topic.id,
            'name': topic.name,
            'liker_count': topic.likers.count(),
            'content': topic.content,
            'time_started': topic.time_started,
            'time_ended': topic.time_ended,
            'deadline': topic.deadline,
            'allow_user': topic.allow_user,
            'user_participator_count': topic.user_participators.count(),
            'status': topic.status,
            'province': topic.province,
            'city': topic.city,
            'unit': topic.unit,
            'user_type': topic.user_type,
            'time_created': topic.time_created,
        })


class TopicStage(View):
    @fetch_object(Topic.enabled, 'topic')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, topic, offset=0, limit=10):
        """获取课题的阶段列表
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

        c = topic.stages.count()
        qs = topic.stages.all().order_by("status")[offset: offset + limit]
        l = [{'id': p.id,
              'status': p.status,
              'time_started': p.time_started,
              'time_ended': p.time_ended,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})


class UserParticipatorList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @fetch_object(Topic.enabled, 'topic')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, topic, offset=0, limit=10, order=1):
        """
        获取报名用户列表
        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                name: 用户昵称
                icon_url: 头像
        """

        k = self.ORDERS[order]
        c = topic.user_participators.count()
        qs = topic.user_participators.all().order_by(
            k)[offset: offset + limit]
        l = [{'id': p.user.id,
              'name': p.user.name,
              'icon_url': p.user.icon} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Topic.enabled, 'topic')
    @require_verification_token
    def post(self, request, topic):
        """报名"""

        if topic.status != 1:
            abort(403, '非报名阶段')
        c = topic.user_participators.count()
        if topic.allow_user != 0 and c >= topic.allow_user:
            abort(403, '参与者已满')
        if topic.province and topic.province != request.user.province:
            abort(403, '地区不符')
        if topic.province and topic.city != request.user.city:
            abort(403, '地区不符')
        if topic.unit and topic.unit != request.user.unit1:
            abort(403, '学校不符')
        if topic.user_type != 0:
            if topic.user_type == 1 and request.user.role != "学生":
                abort(403, '用户角色不符')
            elif topic.user_type == 2 and request.user.role != "教师":
                abort(403, '用户角色不符')
            elif topic.user_type == 3 and request.user.role != "在职":
                abort(403, '用户角色不符')

        if not topic.user_participators.filter(user=request.user).exists():
            topic.user_participators.create(user=request.user)
        abort(200)


class Search(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
        """
        搜索课题

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 课题名包含字段

        :return:
            count: 课题总数
            list: 课题列表
                id: 课题ID
                name: 课题名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
                status:
                province:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        qs = Topic.enabled.filter(name__icontains=kwargs['name'])
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'time_created': a.time_created,
              'status': a.status,
              'province': a.province} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})


class Screen(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(required=False, max_length=20),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'allow_user': forms.IntegerField(required=False, min_value=0),
        'unit1': forms.CharField(required=False, max_length=20),
        'user_type': forms.IntegerField(
            required=False, min_value=0, max_value=3),
        'time_started': forms.DateField(required=False),
        'time_ended': forms.DateField(required=False),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
        """
        筛选课题

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 课题名包含字段
            status: 课题阶段0:前期宣传, 1:报名, 2:结束
            province: 省
            city: 市
            allow_user: 课题允许人数上限,0:不限人数
            unit1: 机构
            user_type: 允许人员身份,0:不限, 1:学生, 2:教师, 3:在职
            time_started: 开始时间下限
            time_ended: 结束时间上限

        :return:
            count: 课题总数
            list: 课题列表
                id: 课题ID
                name: 课题名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
                province:
                status:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        qs = Topic.enabled
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            qs = qs.filter(name__icontains=name)
        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            qs = qs.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            qs = qs.filter(city=city)
        unit1 = kwargs.pop('unit1', '')
        if unit1:
            # 按机构筛选
            qs = qs.filter(unit1=unit1)
        user_type = kwargs.pop('user_type', None)
        if user_type is not None:
            # 按参与者身份筛选
            qs = qs.filter(user_type=user_type)
        status = kwargs.pop('status', None)
        if status is not None:
            # 按课题阶段筛选
            qs = qs.filter(status=status)
        allow_user = kwargs.pop('allow_user', '')
        if allow_user:
            # 按人数上限筛选
            qs = qs.filter(allow_user__lte=allow_user)
        time_started = kwargs.pop('time_started', '')
        if time_started:
            # 按开始时间下限筛选
            qs = qs.filter(time_started__gte=time_started)
        time_ended = kwargs.pop('time_ended', '')
        if time_ended:
            # 按结束时间上限筛选
            qs = qs.filter(time_ended__lte=time_ended)

        qs.all()
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'time_created': a.time_created,
              'province': a.province,
              'status': a.status} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})