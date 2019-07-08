import json

from django import forms
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic import View

from main.models import User
from main.models.activity import *
from main.utils.decorators import validate_args, require_role_token


class AdminActivityAdd(View):

    # @require_role_token
    @validate_args({
        'name': forms.CharField(max_length=50),
        'tags': forms.CharField(max_length=50),
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
        user = User.objects.first()
        if kwargs['type'] not in Activity.TYPES:
            return HttpResponseForbidden()

        activity = Activity(owner_user=user)

        for k in kwargs:
            if k != "stages":
                setattr(activity, k, kwargs[k])
        activity.save()

        stages = json.loads(kwargs['stages'])
        for st in stages:
            activity.stages.create(status=int(st['status']), time_started=st['time_started'],
                                   time_ended=st['time_ended'])

        return JsonResponse({
            'code': 0
        })
