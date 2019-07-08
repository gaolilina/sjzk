#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from web.views.activity import AdminActivityAdd
from web.views.paper import PaperDetail, AnswerThePaper

urls = [
    url(r'^$', AdminActivityAdd.as_view(), name='detail'),
]
