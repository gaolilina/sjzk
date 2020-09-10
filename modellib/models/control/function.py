#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models


class Function(models.Model):
    class Meta:
        abstract = True

    id = models.CharField(max_length=100, null=False, primary_key=True)
    name = models.CharField(max_length=100, null=False)
    enable = models.NullBooleanField(default=True)
    category = models.CharField(max_length=100, default='')
    # 是否需要验证，默认 TRUE，不需要验证的表示所有人都能访问，没有权限限制
    needVerify = models.NullBooleanField(default=True)


class CMSFunction(Function):
    ''' cms 上的功能'''

    class Meta:
        db_table = 'function_cms'
