#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from main.models import Follower


class TeamNeed(models.Model):
    """团队需求信息"""

    TYPE_MEMBER = 0  # 人员需求
    TYPE_OUTSOURCE = 1  # 外包需求
    TYPE_UNDERTAKE = 2  # 承接需求

    team = models.ForeignKey('Team', models.CASCADE, 'needs')
    # 0: member, 1: outsource, 2: undertake
    type = models.IntegerField(db_index=True)
    title = models.TextField(max_length=20)
    # 地区相关
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    county = models.CharField(max_length=20, default='')
    description = models.CharField(default='', max_length=200)
    # 0: pending, 1: completed, 2: removed
    status = models.IntegerField(default=0, db_index=True)
    number = models.IntegerField(default=None, null=True)
    # 领域
    field = models.CharField(default='', max_length=20)
    skill = models.CharField(default='', max_length=20)
    deadline = models.DateField(default=None, null=True, db_index=True)

    age_min = models.IntegerField(default=0)
    age_max = models.IntegerField(default=0)
    gender = models.IntegerField(default=0, db_index=True)
    degree = models.CharField(default='', max_length=20)
    major = models.CharField(default='', max_length=20)
    time_graduated = models.DateField(default=None, null=True)

    cost = models.IntegerField(default=0)
    cost_unit = models.CharField(default='', max_length=1)
    time_started = models.DateField(default=None, null=True)
    time_ended = models.DateField(default=None, null=True)
    # 成员或团队Id
    members = models.CharField(default='', max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_need'
        ordering = ['-time_created']


class TeamNeedFollower(Follower):
    """团队需求关注记录"""

    followed = models.ForeignKey('TeamNeed', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE, 'followed_needs')

    class Meta:
        db_table = 'team_need_follower'


class MemberNeedRequest(models.Model):
    """人员需求的申请加入记录"""

    need = models.ForeignKey('TeamNeed', models.CASCADE, 'member_requests')
    sender = models.ForeignKey('User', models.CASCADE, 'member_requests')
    description = models.TextField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'member_need_request'
        ordering = ['-time_created']


class NeedCooperationRequest(models.Model):
    """外包、承接需求的合作申请记录"""

    need = models.ForeignKey('TeamNeed', models.CASCADE, 'cooperation_requests')
    sender = models.ForeignKey('Team', models.CASCADE, 'cooperation_requests')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'need_cooperation_request'
        ordering = ['-time_created']


class NeedCooperationInvitation(models.Model):
    """外包、承接需求的合作邀请记录"""

    need = models.ForeignKey('TeamNeed', models.CASCADE,
                             'cooperation_invitations')
    invitee = models.ForeignKey('Team', models.CASCADE,
                                'cooperation_invitations')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'need_cooperation_invitation'
        ordering = ['-time_created']
