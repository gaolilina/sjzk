#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class SecurityLog(models.Model):
    """安全日志"""

    username = models.CharField(max_length=128)
    # 接口
    action = models.CharField(max_length=128)
    ip = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    network = models.CharField(max_length=128)
    mac = models.CharField(max_length=128)
    # 手机型号
    model = models.CharField(max_length=128)

    class Meta:
        db_table ='security_log'