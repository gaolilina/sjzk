#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from main.models.common import Follower

class UserNeed(models.Model):
    """用户需求信息"""

    user = models.ForeignKey('main.User', models.CASCADE, 'needs')
    desc = models.CharField(max_length=256)
    # 领域
    field = models.CharField(default='', max_length=256)
    # 点赞
    likers = models.ManyToManyField('main.User', related_name='likeUserNeeds')

    content = models.CharField(default='', max_length=256)
    city = models.CharField(default='', max_length=20)

    time_created = models.DateTimeField(auto_now_add=True, null=True, default=None)
    activity = models.ForeignKey('main.Activity', null=True, default=None)
    competition = models.ForeignKey('main.Competition', null=True, default=None)

    class Meta:
        db_table = 'need_user'
        ordering = ['-time_created']


class NeedFollower(Follower):
    """团队关注记录"""

    followed = models.ForeignKey('UserNeed', models.CASCADE, 'followers')
    follower = models.ForeignKey('main.User', models.CASCADE, 'followed_need')

    class Meta:
        db_table = 'need_user_follower'