#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.generic.base import View

from main.models.role import Role
from util.decorator.auth import app_auth


class RoleList(View):

    @app_auth
    def get(self, request, **kwargs):
        roles = Role.objects.filter(name__isnull=False)
        return JsonResponse({
            'roles': [r.name for r in roles]
        })
