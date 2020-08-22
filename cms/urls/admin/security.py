#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from admin.views.security_log import SecurityLogList

urls = [
    url(r'^$', SecurityLogList.as_view(), name='list'),
]