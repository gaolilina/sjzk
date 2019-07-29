import json

from django import forms

from main.models.activity import *
from main.utils.decorators import require_role_token
from util.base.view import BaseView
from util.decorator.param import validate_args


class AdminActivityAdd(BaseView):

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
    def post(self, request, **kwargs):
        if kwargs['time_ended'] <= kwargs['time_started']:
            return self.fail(1, '开始时间要早于结束时间')
        user = request.user
        if kwargs['type'] not in Activity.TYPES:
            return self.fail(2, '{} 活动类型不存在'.format(kwargs['type']))

        activity = Activity(owner_user=user)

        for k in kwargs:
            if k != "stages":
                setattr(activity, k, kwargs[k])
        activity.save()

        stages = json.loads(kwargs['stages'])
        for st in stages:
            activity.stages.create(status=int(st['status']), time_started=st['time_started'],
                                   time_ended=st['time_ended'])
        return self.success()
