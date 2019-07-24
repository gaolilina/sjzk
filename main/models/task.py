#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class InternalTask(models.Model):
    """内部任务"""

    team = models.ForeignKey('Team', models.CASCADE, 'internal_tasks')
    executor = models.ForeignKey('User', models.CASCADE, 'internal_tasks')

    title = models.CharField(max_length=20)
    content = models.TextField(max_length=100)
    status = models.IntegerField(
        default=0, db_index=True,
        choices=(('等待接受', 0), ('再派任务', 1),
                 ('等待完成', 2), ('等待验收', 3),
                 ('再次提交', 4), ('按时结束', 5),
                 ('超时结束', 6), ('终止', 7)))
    deadline = models.DateField(db_index=True)
    assign_num = models.IntegerField(default=1)
    submit_num = models.IntegerField(default=1)
    finish_time = models.DateTimeField(
        default=None, blank=True, null=True, db_index=True)

    time_created = models.DateTimeField(
        default=timezone.now, db_index=True)

    class Meta:
        db_table = 'internal_task'
        ordering = ['-time_created']


class ExternalTask(models.Model):
    """外部任务"""

    team = models.ForeignKey('Team', models.CASCADE, 'outsource_external_tasks')
    executor = models.ForeignKey(
        'Team', models.CASCADE, 'undertake_external_tasks')

    title = models.CharField(max_length=20)
    content = models.TextField(default='', max_length=100)
    expend = models.IntegerField(default=-1, db_index=True)
    expend_actual = models.IntegerField(default=-1, db_index=True)
    status = models.IntegerField(
        default=0, db_index=True,
        choices=(('等待接受', 0), ('再派任务', 1),
                 ('等待完成', 2), ('等待验收', 3),
                 ('再次提交', 4), ('等待支付', 6),
                 ('再次支付', 7), ('等待确认', 8),
                 ('按时结束', 9), ('超时结束', 10)))
    deadline = models.DateField(db_index=True)
    assign_num = models.IntegerField(default=1)
    submit_num = models.IntegerField(default=1)
    pay_num = models.IntegerField(default=1)
    pay_time = models.DateTimeField(
        default=None, blank=True, null=True, db_index=True)
    finish_time = models.DateTimeField(
        default=None, blank=True, null=True, db_index=True)

    time_created = models.DateTimeField(
        default=timezone.now, db_index=True)

    class Meta:
        db_table = 'external_task'
        ordering = ['-time_created']