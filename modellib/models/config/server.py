#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class ServerConfig(models.Model):
    class Meta:
        db_table = 'config_server'

    # 环信 access_token
    huanxin_token = models.CharField(max_length=200, default='')

    # 同 IP 两次访问的时间间隔，单位毫秒，即平均 qps
    ip_limit_time = models.IntegerField(default=500)
    # 同 IP 超速访问容忍的次数
    ip_limit_count = models.IntegerField(default=10)
    # 同 IP 超速访问 容忍次数的时间，单位秒，即峰值 qps
    ip_limit_time_max = models.IntegerField(default=2)
