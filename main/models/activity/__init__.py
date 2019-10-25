#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from main.models import EnabledManager, Comment

__all__ = ['Activity', 'ActivityStage', 'ActivityComment']


class Activity(models.Model):
    """活动基本信息"""

    # 活动状态
    # 审核中
    STATE_CHECKING = 0
    # 通过
    STATE_PASSED = 100
    # 未通过
    STATE_NO = 10

    # 活动类型
    # 会议
    TYPE_CONFERENCE = 0
    # 讲座
    TYPE_LECTURE = 1
    # 培训
    TYPE_TRAINING = 2

    TYPES = [TYPE_CONFERENCE, TYPE_LECTURE, TYPE_TRAINING]

    name = models.CharField(max_length=50, null=True)
    # 活动状态：
    state = models.IntegerField(default=STATE_CHECKING)
    # 活动类型
    type = models.IntegerField(default=TYPE_CONFERENCE)
    # 活动成果
    achievement = models.CharField(max_length=100, default='')
    status = models.IntegerField(default=0, db_index=True)
    content = models.CharField(max_length=1000, null=True)
    deadline = models.DateTimeField(db_index=True, null=True)
    time_started = models.DateTimeField(db_index=True, null=True)
    time_ended = models.DateTimeField(db_index=True, null=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # 活动允许的人数上限，0：不限
    allow_user = models.IntegerField(default=0, db_index=True)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    unit = models.CharField(max_length=20, default='')
    # 领域
    field = models.CharField(max_length=20, default='')
    # 0:不限, 1:学生, 2:教师, 3:在职
    user_type = models.IntegerField(default=0, db_index=True)
    is_enabled = models.BooleanField(default=True)

    owner_user = models.ForeignKey('User', related_name='+', null=True)
    lab_sponsor = models.ForeignKey('Lab', related_name='lab_sponsored_activities', null=True)
    expert_sponsor = models.ForeignKey('User', related_name='expert_sponsored_activities', null=True)

    # 专家
    experts = models.ManyToManyField('User', related_name='activities_as_expert', null=True, default=None)
    # 费用二维码
    expense = models.CharField(max_length=100, default='')
    # 标签
    tags = models.CharField(max_length=255, default='')

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'activity'
        ordering = ['-time_created']

    def get_current_state(self):
        time_now = timezone.now()
        # 结束
        if time_now > self.time_ended:
            return ActivityStage.STAGE_END
        # 未开始
        if time_now < self.time_started:
            return ActivityStage.STAGE_NO_STARTED
        stages = self.stages.all()
        stage_apply = None
        stage_pro = None
        for s in stages:
            if s.status == ActivityStage.STAGE_APPLY:
                stage_apply = s
            elif s.status == ActivityStage.STAGE_PROPAGANDA:
                stage_pro = s
        # 报名
        if stage_apply is not None and self.is_in_stage(stage_apply, time_now):
            return ActivityStage.STAGE_APPLY
        # 宣传
        if stage_pro is not None and self.is_in_stage(stage_pro, time_now):
            return ActivityStage.STAGE_PROPAGANDA
        # 进行中，不知道哪个阶段
        return ActivityStage.STATE_RUNNING

    def is_in_stage(self, stage, time):
        return stage.time_started <= time <= stage.time_ended


class ActivityStage(models.Model):
    """活动阶段"""

    # 活动阶段
    # 未开始
    STAGE_NO_STARTED = -1
    # 宣传
    STAGE_PROPAGANDA = 0
    # 报名
    STAGE_APPLY = 1
    # 结束
    STAGE_END = 2
    # 进行中
    STATE_RUNNING = 3

    activity = models.ForeignKey('Activity', models.CASCADE, 'stages')
    status = models.IntegerField(default=0, db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'activity_stage'


class ActivityComment(Comment):
    """活动评论"""

    entity = models.ForeignKey('Activity', models.CASCADE, 'comments')

    class Meta:
        db_table = 'activity_comment'
        ordering = ['time_created']
