#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.generic.base import View

from util.decorator.auth import app_auth
from modellib.models.config import ApplicationConfig
from modellib.models.paper import Paper


class PaperList(View):

    @app_auth
    def get(self, request, **kwargs):
        appconfig = ApplicationConfig.objects.all().first()
        papers = Paper.objects.filter(enable=True)[:appconfig.paper_count]
        return JsonResponse({
            'style': appconfig.paper_style,
            'list': [{
                'id': p.id,
                'name': p.name,
                'url': appconfig.paper_url
            } for p in papers],
            'code': 0
        })
