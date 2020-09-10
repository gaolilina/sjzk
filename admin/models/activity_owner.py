#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models

__all__ = ['ActivityOwner']


class ActivityOwner(models.Model):
    """活动创建者"""

    activity = models.ForeignKey('main.Activity', models.CASCADE, 'owner')
    user = models.ForeignKey('AdminUser', models.CASCADE, '+')

    class Meta:
        db_table = 'activity_owner'
