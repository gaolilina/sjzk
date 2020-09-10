#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models


class IPLimit(models.Model):
    TYPE_APP = 0
    TYPE_WEB = 1
    TYPE_ADMIN = 2
    TYPE_CMS = 3

    ip = models.CharField(max_length=40, default='')
    type = models.IntegerField(default=TYPE_CMS)

    # 最后一次访问通过的时间
    last_time = models.DateTimeField(auto_now_add=True)
    # 出现超速的时间
    first_time = models.DateTimeField(null=True, default=None)
    illegal_count = models.IntegerField(default=0)
    is_lock = models.BooleanField(default=False)

    code = models.CharField(max_length=10, default='')

    class Meta:
        db_table = 'ip_limit'
