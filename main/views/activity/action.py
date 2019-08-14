#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Activity, ActivityStage
from main.utils import abort
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


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
            abort(403, '您未报名活动，无法签到')
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

        if activity.get_current_state() != ActivityStage.STAGE_APPLY:
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
