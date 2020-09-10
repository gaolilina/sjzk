#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models


class ComboBox(models.Model):
    """下拉列表结构"""
    key = models.CharField(max_length=254, default='');
    value = models.CharField(max_length=254, default='');
    parent = models.ForeignKey('ComboBox', related_name='children', null=True, default=None);
    enable = models.BooleanField(default=True);

    class Meta:
        db_table = 'comboBox'