#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from web.views.activity import AdminActivityAdd, ActivityAnalysis, ActivityModify

urlpatterns = [
    url(r'^$', AdminActivityAdd.as_view()),
    url(r'^(?P<activity_id>\d+)/analysis/$', ActivityAnalysis.as_view()),
    url(r'^(?P<activity_id>\d+)/$', ActivityModify.as_view()),
]
