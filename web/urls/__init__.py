#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from web.urls import paper, activity

urlpatterns = [
    url(r'^paper/', include(paper.urls, namespace='paper')),
    url(r'^activity/', include(activity.urls, namespace='activity')),
]
