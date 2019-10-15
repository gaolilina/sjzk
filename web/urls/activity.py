#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from web.views.activity.analysis import ActivityAnalysis
from web.views.activity.create_edit import AdminActivityAdd, ActivityModify
from web.views.activity.experts import ActivityExpert
from web.views.activity.list import MyCreatedActivityList

urlpatterns = [
    url(r'^$', AdminActivityAdd.as_view()),
    url(r'^created/$', MyCreatedActivityList.as_view()),
    url(r'^(?P<activity_id>\d+)/analysis/$', ActivityAnalysis.as_view()),
    url(r'^(?P<activity_id>\d+)/$', ActivityModify.as_view()),
    url(r'^(?P<activity_id>\d+)/expert/$', ActivityExpert.as_view()),
]
