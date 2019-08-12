#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from django.db import models
from django.utils import timezone

from main.models import Liker, Follower, Favorer

'''活动相关人员'''


class ActivitySign(models.Model):
    class Meta:
        db_table = 'activity_sign'

    activity = models.ForeignKey('Activity', related_name='signers')
    user = models.ForeignKey('User', related_name='+')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)


class ActivityUserParticipator(models.Model):
    """活动参与者（用户）"""

    activity = models.ForeignKey(
        'Activity', models.CASCADE, 'user_participators')
    user = models.ForeignKey('User', models.CASCADE, 'activities')

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'activity_user_participator'
        ordering = ['-time_created']


class ActivityLiker(Liker):
    """活动点赞记录"""

    liked = models.ForeignKey('Activity', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_activities')

    class Meta:
        db_table = 'activity_liker'


class ActivityFollower(Follower):
    """活动关注记录"""

    followed = models.ForeignKey('Activity', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE,
                                 'followed_activities')

    class Meta:
        db_table = 'activity_follower'


class ActivityFavorer(Favorer):
    """活动收藏记录"""

    favored = models.ForeignKey('Activity', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_activities')

    class Meta:
        db_table = 'activity_favorer'
