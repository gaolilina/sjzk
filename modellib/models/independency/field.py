#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models


class Field(models.Model):
    class Meta:
        db_table = 'field'

    name = models.CharField(max_length=254, default='', unique=True)
    parent = models.ForeignKey('Field', related_name='children', null=True, default=None)
    enable = models.BooleanField(default=True)
