#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from web.urls import paper

urlpatterns = [
    url(r'^paper/', include(paper.urls, namespace='paper')),
]
