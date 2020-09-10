#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models


class AppEvent(models.Model):
    class Meta:
        db_table = 'event_app'

    # url 的正则表达式
    url = models.CharField(max_length=254, default='')
    # 事件名称
    name = models.CharField(max_length=254, primary_key=True)
    # 获得的奖励
    grade = models.IntegerField()
