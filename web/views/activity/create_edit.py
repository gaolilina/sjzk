import json
from datetime import datetime

from django import forms

from main.models import Activity, ActivityStage
from main.utils.decorators import require_role_token
from util.base.view import BaseView
from util.decorator.param import validate_args, fetch_object
from web.views.activity import activity_owner


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
        time_start = kwargs['time_started']
        time_end = kwargs['time_ended']
        if time_end <= time_start:
            return self.fail(1, '开始时间要早于结束时间')
        # 活动类型检查
        if kwargs['type'] not in Activity.TYPES:
            return self.fail(2, '{} 活动类型不存在'.format(kwargs['type']))
        # 活动阶段检查
        stages = json.loads(stages)
        if type(stages) is not list or len(stages) <= 0:
            return self.fail(3, '活动阶段不能为空')
        for stage in stages:
            code, desc = check_stage(stage, time_start, time_end)
            if code > 0:
                return self.fail(code, desc)

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
            'type': activity.type,
            'tags': activity.tags,
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
                'phone': ex.phone_number,
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
    @activity_owner()
    def post(self, request, activity, stages=None, **kwargs):
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
            for stage in stages:
                code, desc = check_stage(stage, time_start, time_end)
                if code > 0:
                    return self.fail(code, desc)

        for k in kwargs:
            setattr(activity, k, kwargs[k])
        activity.save()

        if stages:
            ActivityStage.objects.filter(activity=activity).delete()
            for st in stages:
                activity.stages.create(status=int(st['status']), time_started=st['time_started'],
                                       time_ended=st['time_ended'])
        return self.success()


def check_stage(stage, activity_start, activity_end):
    # 状态标识
    status = stage['status']
    if status not in ActivityStage.ALL_STAGES:
        return 4, '不存在 {} 这种活动阶段'.format(status)
    # 开始时间
    stage_start = stage['time_started']
    try:
        stage_start = format_time(stage_start)
    except ValueError:
        return 5, '{}阶段的开始时间格式错误'.format(ActivityStage.ALL_STAGES_STR[status])
    if not (activity_start <= stage_start <= activity_end):
        return 6, '{}阶段的开始时间应在活动开始时间和结束时间之间'.format(ActivityStage.ALL_STAGES_STR[status])
    # 结束时间
    stage_end = stage['time_ended']
    try:
        stage_end = format_time(stage_end)
    except ValueError:
        return 7, '{}阶段的结束时间格式错误'.format(ActivityStage.ALL_STAGES_STR[status])
    if not (activity_start <= stage_end <= activity_end):
        return 8, '{}阶段的结束时间应在活动开始时间和结束时间之间'.format(ActivityStage.ALL_STAGES_STR[status])
    # 开始和结束时间对比
    if stage_end < stage_start:
        return 9, '{}阶段的结束时间应晚于开始时间'.format(ActivityStage.ALL_STAGES_STR[status])
    return 0, ''


def format_time(time_str):
    if len(time_str) > 16:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    elif len(time_str) > 10:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    else:
        return datetime.strptime(time_str, '%Y-%m-%d')
