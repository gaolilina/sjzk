#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from web.urls import paper, activity, field

urlpatterns = [
    url(r'^paper/', include(paper.urls)),
    url(r'^activity/', include(activity.urls)),
    url(r'^field/', include(field.urls)),
]
