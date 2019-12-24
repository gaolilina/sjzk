#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class ServerConfig(models.Model):
    class Meta:
        db_table = 'config_server'

    # 环信 access_token
    huanxin_token = models.CharField(max_length=200, default='')

    # 同 IP 两次访问的时间间隔，单位毫秒
    ip_limit_time = models.IntegerField(default=500)
    # 同 IP 超速访问容忍的次数
    ip_limit_count = models.IntegerField(default=10)
