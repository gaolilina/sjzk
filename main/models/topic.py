#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment, Liker, Follower, Favorer


__all__ = ['Topic', 'TopicStage', 'TopicUserParticipator',
           'TopicComment', 'TopicLiker', 'TopicFollower',
           'TopicFavorer']


class Topic(models.Model):
    """活动基本信息"""

    name = models.CharField(max_length=50)
    # 活动当前阶段：0:前期宣传, 1:报名, 2:结束
    status = models.IntegerField(default=0, db_index=True)
    content = models.CharField(max_length=1000)
    deadline = models.DateTimeField(db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # 活动允许的人数上限，0：不限
    allow_user = models.IntegerField(default=0, db_index=True)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    unit = models.CharField(max_length=20, default='')
    # 0:不限, 1:学生, 2:教师, 3:在职
    user_type = models.IntegerField(default=0, db_index=True)
    is_enabled = models.BooleanField(default=True)

    lab_sponsor = models.ForeignKey('Lab', related_name='lab_sponsored_topics', null=True)
    expert_sponsor = models.ForeignKey('User', related_name='expert_sponsored_topics', null=True)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'topic'
        ordering = ['-time_created']


class TopicStage(models.Model):
    """活动阶段"""

    topic = models.ForeignKey('Topic', models.CASCADE, 'stages')
    # 0:前期宣传, 1:报名, 2:结束
    status = models.IntegerField(default=0, db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'topic_stage'


class TopicUserParticipator(models.Model):
    """活动参与者（用户）"""

    topic = models.ForeignKey(
        'Topic', models.CASCADE, 'user_participators')
    user = models.ForeignKey('User', models.CASCADE, 'topics')

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'topic_user_participator'
        ordering = ['-time_created']


class TopicComment(Comment):
    """活动评论"""

    entity = models.ForeignKey('Topic', models.CASCADE, 'comments')

    class Meta:
        db_table = 'topic_comment'
        ordering = ['time_created']


class TopicLiker(Liker):
    """活动点赞记录"""

    liked = models.ForeignKey('Topic', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_topics')

    class Meta:
        db_table = 'topic_liker'


class TopicFollower(Follower):
    """活动关注记录"""

    followed = models.ForeignKey('Topic', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE,
                                 'followed_topics')

    class Meta:
        db_table = 'topic_follower'

class TopicFavorer(Favorer):
    """活动收藏记录"""

    favored = models.ForeignKey('Topic', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_topics')

    class Meta:
        db_table = 'topic_favorer'
