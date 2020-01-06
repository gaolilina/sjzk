#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from web.urls import paper, activity, field, lottery, competition, need_user, me, friend

urlpatterns = [
    url(r'^paper/', include(paper.urls)),
    url(r'^activity/', include(activity)),
    url(r'^field/', include(field.urls)),
    url(r'^lottery/', include(lottery)),
    url(r'^competition/', include(competition)),
    url(r'^need/user/', include(need_user)),
    url(r'^me/', include(me)),
    url(r'^friend/', include(friend)),
]
