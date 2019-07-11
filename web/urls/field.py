#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from web.views.field import FieldList, FieldDelete

urls = [
    url(r'^$', FieldList.as_view()),
    url(r'^(?P<field_id>\d+)/$', FieldDelete.as_view()),
]
