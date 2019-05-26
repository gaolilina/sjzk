#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from web.views.paper import PaperDetail, AnswerThePaper

urls = [
    url(r'^(?P<paper_id>\d+)/$', PaperDetail.as_view(), name='detail'),
    url(r'^(?P<paper_id>\d+)/answer/$', AnswerThePaper.as_view(), name='answer'),
]
