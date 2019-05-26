#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from admin.views.paper import PaperList, PaperDetail, PaperSwitch

urls = [
    url(r'^$', PaperList.as_view(), name='list'),
    url(r'^(?P<paper_id>\d+)/$', PaperDetail.as_view(), name='detail'),
    url(r'^(?P<paper_id>\d+)/switch/$', PaperSwitch.as_view(), name='switch'),
]
