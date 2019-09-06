import json

from django import forms

from main.models import User
from main.models.activity import *
from main.models.activity.people import ActivityUserParticipator
from main.utils.decorators import require_role_token
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class AdminActivityAdd(BaseView):
    """活动创建"""

    @require_role_token
    @validate_args({
        'name': forms.CharField(max_length=50),
        'tags': forms.CharField(max_length=50),
        'field': forms.CharField(max_length=50),
        'content': forms.CharField(max_length=1000),
        'time_started': forms.DateTimeField(),
        'time_ended': forms.DateTimeField(),
        'allow_user': forms.IntegerField(),
        'status': forms.IntegerField(),
        'type': forms.IntegerField(),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(),
        'stages': forms.CharField(),
    })
    def post(self, request, stages, **kwargs):
        # 活动时间的检查
        if kwargs['time_ended'] <= kwargs['time_started']:
            return self.fail(1, '开始时间要早于结束时间')
        # 活动类型检查
        if kwargs['type'] not in Activity.TYPES:
            return self.fail(2, '{} 活动类型不存在'.format(kwargs['type']))
        # 活动阶段检查
        stages = json.loads(stages)
        if type(stages) is not list or len(stages) <= 0:
            return self.fail(3, '活动阶段不能为空')

        user = request.user
        activity = Activity(owner_user=user)

        for k in kwargs:
            setattr(activity, k, kwargs[k])
        activity.save()

        for st in stages:
            activity.stages.create(status=int(st['status']), time_started=st['time_started'],
                                   time_ended=st['time_ended'])
        return self.success()


class ActivityModify(BaseView):
    """活动详情"""

    @require_role_token
    @validate_args({
        'activity_id': forms.IntegerField(),
    })
    @fetch_object(Activity.objects, 'activity')
    def get(self, request, activity, **kwargs):
        owner = activity.owner_user
        return self.success({
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
            'owner': owner.name if owner is not None else "",
            'owner_id': owner.id if owner is not None else -1,
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

    @require_role_token
    @validate_args({
        'activity_id': forms.IntegerField(),
        'name': forms.CharField(max_length=50, required=False),
        'tags': forms.CharField(max_length=50, required=False),
        'field': forms.CharField(max_length=50, required=False),
        'content': forms.CharField(max_length=1000, required=False),
        'time_started': forms.DateTimeField(required=False),
        'time_ended': forms.DateTimeField(required=False),
        'allow_user': forms.IntegerField(required=False),
        'status': forms.IntegerField(required=False),
        'type': forms.IntegerField(required=False),
        'province': forms.CharField(max_length=20, required=False),
        'city': forms.CharField(max_length=20, required=False),
        'unit': forms.CharField(max_length=20, required=False),
        'user_type': forms.IntegerField(required=False),
        'stages': forms.CharField(required=False),
    })
    @fetch_object(Activity.objects, 'activity')
    def post(self, request, activity, stages=None, **kwargs):
        if activity.owner_user != request.user:
            return self.fail(5, '只有创建者才能修改')
        if activity.state != Activity.STATE_NO:
            return self.fail(4, '只有审核未通过的活动才能修改')
        # 活动时间的检查
        time_start = kwargs.get('time_started') or activity.time_started
        time_end = kwargs.get('time_ended') or activity.time_ended
        if time_end <= time_start:
            return self.fail(1, '开始时间要早于结束时间')
        # 活动类型检查
        if 'type' in kwargs and kwargs['type'] not in Activity.TYPES:
            return self.fail(2, '{} 活动类型不存在'.format(kwargs['type']))
        # 活动阶段检查
        if stages:
            stages = json.loads(stages)
            if type(stages) is not list or len(stages) <= 0:
                return self.fail(3, '活动阶段不能为空')

        for k in kwargs:
            setattr(activity, k, kwargs[k])
        activity.state = Activity.STATE_CHECKING
        activity.save()

        if stages:
            activity.stages.clear()
            for st in stages:
                activity.stages.create(status=int(st['status']), time_started=st['time_started'],
                                       time_ended=st['time_ended'])
        return self.success()


class ActivityAnalysis(BaseView):
    """活动分析"""

    KEY_ROLE = 'role'
    KEY_GENDER = 'gender'
    KEY_PROFESSION = 'profession'
    KEY_PROVINCE = 'province'
    KEY_UNIT = 'unit'

    KEY_OTHER = '其他'
    KEY_EMPTY = '未设置'

    KEY_SCHOOL = '学校'
    KEY_HOSPITAL = '医院'
    KEY_COMPANY = '企业'

    KEY_SCHOOLS = ['学校', '大学', '中学', '小学']
    KEY_HOSPITALS = ['医院']
    KEY_COMPANIES = ['公司']

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField()
    })
    @fetch_object(Activity.objects, 'activity')
    def get(self, request, activity, **kwargs):
        if activity.owner_user != request.user:
            return self.fail(1, '您不是活动的创办者')
        result = self.__init_result_template()
        users = ActivityUserParticipator.objects.filter(activity=activity)
        for u in users:
            self.__analysis_on_person(u.user, result)
        result['sum'] = users.count()
        return self.success(result)

    def __analysis_on_person(self, user, result):
        # 性别
        result[ActivityAnalysis.KEY_GENDER][User.GENDERS[user.gender]] += 1
        # 角色
        if user.is_role_verified != 2 or not user.role:
            # 未设置
            result[ActivityAnalysis.KEY_ROLE][ActivityAnalysis.KEY_EMPTY] += 1
        elif user.role in result[ActivityAnalysis.KEY_ROLE]:
            result[ActivityAnalysis.KEY_ROLE][user.role] += 1
        else:
            # 其他角色
            result[ActivityAnalysis.KEY_ROLE][ActivityAnalysis.KEY_OTHER] += 1
        # 专业
        if not user.profession:
            result[ActivityAnalysis.KEY_PROFESSION][ActivityAnalysis.KEY_EMPTY] += 1
        elif user.profession in result[ActivityAnalysis.KEY_PROFESSION]:
            result[ActivityAnalysis.KEY_PROFESSION][user.profession] += 1
        else:
            result[ActivityAnalysis.KEY_PROFESSION][user.profession] = 1

        # 地区
        if not user.province:
            result[ActivityAnalysis.KEY_PROVINCE][ActivityAnalysis.KEY_EMPTY] += 1
        elif user.province in result[ActivityAnalysis.KEY_PROVINCE]:
            result[ActivityAnalysis.KEY_PROVINCE][user.province] += 1
        else:
            result[ActivityAnalysis.KEY_PROVINCE][user.province] = 1

        # 组织类型
        result[ActivityAnalysis.KEY_UNIT][self.__get_unit_category(user.unit1)] += 1
        pass

    def __init_result_template(self):
        return {
            ActivityAnalysis.KEY_ROLE: {
                '专家': 0,
                '学生': 0,
                ActivityAnalysis.KEY_OTHER: 0,
                ActivityAnalysis.KEY_EMPTY: 0,
            },
            ActivityAnalysis.KEY_GENDER: {
                '男': 0,
                '女': 0,
                '未知': 0,
            },
            ActivityAnalysis.KEY_PROFESSION: {
                ActivityAnalysis.KEY_EMPTY: 0,
            },
            ActivityAnalysis.KEY_PROVINCE: {},
            ActivityAnalysis.KEY_UNIT: {
                ActivityAnalysis.KEY_SCHOOL: 0,
                ActivityAnalysis.KEY_COMPANY: 0,
                ActivityAnalysis.KEY_HOSPITAL: 0,
                ActivityAnalysis.KEY_OTHER: 0,
                ActivityAnalysis.KEY_EMPTY: 0,
            },
        }

    def __get_unit_category(self, unit):
        if not unit:
            return ActivityAnalysis.KEY_EMPTY
        unit = ''
        # 判断学校
        for k in ActivityAnalysis.KEY_SCHOOLS:
            if k in unit:
                return ActivityAnalysis.KEY_SCHOOL
        # 判断企业
        for k in ActivityAnalysis.KEY_COMPANIES:
            if k in unit:
                return ActivityAnalysis.KEY_COMPANY
        # 判断医院
        for k in ActivityAnalysis.KEY_HOSPITALS:
            if k in unit:
                return ActivityAnalysis.KEY_HOSPITAL
        return ActivityAnalysis.KEY_OTHER
        pass
