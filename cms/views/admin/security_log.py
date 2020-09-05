#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic.base import View

from admin.models.security_log import SecurityLog
from admin.utils.decorators import require_role
from util.decorator.param import old_validate_args
from util.decorator.auth import admin_auth


class SecurityLogList(View):

    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'username': forms.CharField(max_length=50, required=False),
        'ip': forms.CharField(max_length=50, required=False),
        'action': forms.CharField(max_length=50, required=False),
        'location': forms.CharField(max_length=50, required=False),
        'model': forms.CharField(max_length=50, required=False),
    })
    def get(self, request, **kwargs):
        params_list = ['username', 'ip', 'action', 'model']
        params = {}
        for p in params_list:
            if p in kwargs and kwargs.get(p) is not None and len(kwargs.get(p)) > 0:
                params[p] = kwargs.get(p)
        template = loader.get_template("net_police/net_log.html")
        context = Context({
            'user': request.user,
            'list': SecurityLog.objects.filter(**params) if len(params) != 0 else SecurityLog.objects.all()})
        return HttpResponse(template.render(context))
