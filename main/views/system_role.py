#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.generic.base import View

from main.models.role import Role
from main.utils.decorators import require_token


class RoleList(View):

    @require_token
    def get(self, request, **kwargs):
        roles = Role.objects.all()
        return JsonResponse({
            'roles': [r.name for r in roles]
        })
