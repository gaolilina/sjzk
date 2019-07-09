#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from main.models import Liker, Comment, Favorer


class Action(models.Model):
    """动态"""

    entity = None
    action = models.CharField(max_length=20)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # user, team, member_need, outsource_need, undertake_need
    object_type = models.CharField(max_length=20)
    object_id = models.IntegerField(db_index=True)
    # user, team, member_need, outsource_need, undertake_need
    related_object_type = models.CharField(default=None, null=True, max_length=20)
    related_object_id = models.IntegerField(default=None, null=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-time_created']


class UserAction(Action):
    """用户动态"""

    entity = models.ForeignKey('User', models.CASCADE, 'actions')

    class Meta:
        db_table = 'user_action'


class UserActionLiker(Liker):
    """用户动态点赞记录"""

    liked = models.ForeignKey('UserAction', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_user_actions')

    class Meta:
        db_table = 'user_action_liker'


class UserActionComment(Comment):
    """用户动态评论记录"""

    entity = models.ForeignKey('UserAction', models.CASCADE, 'comments')

    class Meta:
        db_table = 'user_action_comment'
        ordering = ['time_created']


class TeamAction(Action):
    """团队动态"""

    entity = models.ForeignKey('Team', models.CASCADE, 'actions')

    class Meta:
        db_table = 'team_action'


class TeamActionLiker(Liker):
    """团队动态点赞记录"""

    liked = models.ForeignKey('TeamAction', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_team_actions')

    class Meta:
        db_table = 'team_action_liker'


class TeamActionComment(Comment):
    """团队动态评论记录"""

    entity = models.ForeignKey('TeamAction', models.CASCADE, 'comments')

    class Meta:
        db_table = 'team_action_comment'
        ordering = ['time_created']


class LabAction(Action):
    """团队动态"""

    entity = models.ForeignKey('Lab', models.CASCADE, 'actions')

    class Meta:
        db_table = 'lab_action'


class LabActionLiker(Liker):
    """团队动态点赞记录"""

    liked = models.ForeignKey('LabAction', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_lab_actions')

    class Meta:
        db_table = 'lab_action_liker'


class LabActionComment(Comment):
    """团队动态评论记录"""

    entity = models.ForeignKey('LabAction', models.CASCADE, 'comments')

    class Meta:
        db_table = 'lab_action_comment'
        ordering = ['time_created']


class TeamActionFavorer(Favorer):
    """团队动态收藏记录"""

    favored = models.ForeignKey('TeamAction', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_team_actions')

    class Meta:
        db_table = 'team_action_favorer'


class UserActionFavorer(Favorer):
    """用户动态收藏记录"""

    favored = models.ForeignKey('UserAction', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_user_actions')

    class Meta:
        db_table = 'user_action_favorer'


class LabActionFavorer(Favorer):
    """团队动态收藏记录"""

    favored = models.ForeignKey('LabAction', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_lab_actions')

    class Meta:
        db_table = 'lab_action_favorer'