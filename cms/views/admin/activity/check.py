#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms

from main.models import Activity
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import fetch_object, validate_args
from util.decorator.permission import admin_permission


class ActivityCheck(BaseView):
    @cms_auth
    @admin_permission('check_activity')
    @validate_args({
        'activity_id': forms.IntegerField(),
        'result': forms.BooleanField(),
    })
    @fetch_object(Activity.objects, 'activity')
    def post(self, request, activity, result, **kwargs):
        if activity.state == Activity.STATE_NO:
            return self.fail(1, '活动已被拒绝，需要用户重新提交材料')
        if activity.state == Activity.STATE_PASSED:
            return self.success()
        if activity.state == Activity.STATE_CHECKING:
            Activity.objects.filter(id=activity.id) \
                .update(state=Activity.STATE_PASSED if result else Activity.STATE_NO)
            return self.success()