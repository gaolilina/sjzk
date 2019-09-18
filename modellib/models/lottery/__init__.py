#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models


class Lottery(models.Model):
    class Meta:
        db_table = 'lottery'

    # 抽奖名称
    name = models.CharField(max_length=100)
    # 创建抽奖的用户
    user = models.ForeignKey('main.User', related_name='create_lottery')
    # 是否已结束
    finished = models.BooleanField(default=False)


class LotteryParticipant(models.Model):
    class Meta:
        db_table = 'lottery_participant'

    # 关联的实际的创易用户
    user = models.ForeignKey('main.User', related_name='join_lottery')
    # 关联的抽奖
    lottery = models.ForeignKey('Lottery', related_name='users')
    # 是否中奖
    is_victory = models.BooleanField(default=False)
    # 是否已处理
    is_handled = models.BooleanField(default=False)
    # 信息
    info = models.CharField(max_length=100, default='')
