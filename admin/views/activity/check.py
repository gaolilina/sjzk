#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from admin.utils.decorators import require_cookie, require_role
from main.models import Activity
from main.utils import abort
from main.utils.decorators import fetch_object, validate_args


class ActivityCheck(View):

    @require_cookie
    @require_role('xyz')
    @validate_args({
        'activity_id': forms.IntegerField(),
        'result': forms.BooleanField(required=False),
    })
    @fetch_object(Activity.objects, 'activity')
    def post(self, request, activity, result, **kwargs):
        if activity.state == Activity.STATE_CHECKING:
            Activity.objects.filter(id=activity.id) \
                .update(state=Activity.STATE_PASSED if result else Activity.STATE_NO)
            return JsonResponse({})
        else:
            abort(403, "重新提交材料")
