#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class ApplicationConfig(models.Model):
    class Meta:
        db_table = 'config_application'

    # app 端显示调查问卷的数量
    paper_count = models.IntegerField(default=3)
    # 显示调查问卷的样式
    paper_style = models.CharField(max_length=25, default='list')
    # 调查问卷 url
    paper_url = models.CharField(max_length=100, default='/static/paper/detail.html')
