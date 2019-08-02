from django import forms
from django.http import JsonResponse
from django.views.generic import View

from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object
from main.models import Activity
from main.utils import abort
from main.utils.decorators import *

__all__ = ['UserParticipatorList', 'Screen', 'ActivitySignList']


class ActivitySignList(View):
    """
    活动签到
    """

    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, activity, offset=0, limit=10):
        c = activity.signers.count()
        qs = activity.signers.all()[offset: offset + limit]
        l = [{'id': p.user.id,
              'name': p.user.name,
              'icon_url': p.user.icon,
              'time': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Activity.enabled, 'activity')
    @require_verification_token
    def post(self, request, activity):
        if activity.user_participators.filter(user=request.user).exists():
            activity.signers.create(user=request.user)
        else:
            abort(403)
        abort(200)


class UserParticipatorList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, activity, offset=0, limit=10, order=1):
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
        c = activity.user_participators.count()
        qs = activity.user_participators.all().order_by(
            k)[offset: offset + limit]
        l = [{'id': p.user.id,
              'name': p.user.name,
              'icon_url': p.user.icon} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Activity.enabled, 'activity')
    @require_verification_token
    def post(self, request, activity):
        """报名"""

        if activity.status != 1:
            abort(403, '非报名阶段')
        c = activity.user_participators.count()
        if activity.allow_user != 0 and c >= activity.allow_user:
            abort(403, '参与者已满')
        if activity.province and activity.province != request.user.province:
            abort(403, '地区不符')
        if activity.province and activity.city != request.user.city:
            abort(403, '地区不符')
        if activity.unit and activity.unit != request.user.unit1:
            abort(403, '学校不符')
        if activity.user_type != 0:
            if activity.user_type == 1 and request.user.role != "学生":
                abort(403, '用户角色不符')
            elif activity.user_type == 2 and request.user.role != "教师":
                abort(403, '用户角色不符')
            elif activity.user_type == 3 and request.user.role != "在职":
                abort(403, '用户角色不符')

        if not activity.user_participators.filter(user=request.user).exists():
            activity.user_participators.create(user=request.user)
        abort(200)


class Screen(View):
    """
    筛选
    """
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
        筛选活动

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 活动名包含字段
            status: 活动阶段0:前期宣传, 1:报名, 2:结束
            province: 省
            city: 市
            allow_user: 活动允许人数上限,0:不限人数
            unit1: 机构
            user_type: 允许人员身份,0:不限, 1:学生, 2:教师, 3:在职
            time_started: 开始时间下限
            time_ended: 结束时间上限

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
                province:
                status:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        qs = Activity.enabled
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
            # 按活动阶段筛选
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