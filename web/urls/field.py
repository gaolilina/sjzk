#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from web.views.field import FieldList

urls = [
    url(r'^$', FieldList.as_view()),
]
