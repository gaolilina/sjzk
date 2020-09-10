#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

__all__ = ['OperationLog']


class OperationLog(models.Model):
    """活动创建者"""

    time = models.DateTimeField(default=timezone.now, db_index=True)
    table = models.CharField(max_length=128)
    data_id = models.IntegerField()
    # 1 - 修改, 2 - 增加, 3 - 删除
    operate_type = models.IntegerField()
    user = models.ForeignKey('AdminUser', models.CASCADE, '+')

    class Meta:
        db_table = 'operation_log'
