#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class Role(models.Model):
    """角色"""

    class Meta:
        db_table = 'role'
        ordering = ['order']

    name = models.CharField(max_length=32, null=True, default=None)
    order = models.IntegerField(default=0)
    param = models.OneToOneField('System', related_name='role')
