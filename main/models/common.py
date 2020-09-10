#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

__all__ = ['Comment', 'Follower', 'Liker', 'Tag', 'Visitor', 'Favorer']


class Comment(models.Model):
    """评论"""

    entity = None
    author = models.ForeignKey('User', models.CASCADE, '+')
    content = models.CharField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    likers = models.ManyToManyField('User', related_name='+')

    class Meta:
        abstract = True
        ordering = ['-time_created']


class Follower(models.Model):
    """关注"""

    followed = None
    follower = None
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-time_created']


class Liker(models.Model):
    """点赞"""

    liked = None
    liker = None
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-time_created']


class Tag(models.Model):
    """标签记录"""

    entity = None
    name = models.CharField(max_length=20)
    order = models.IntegerField(db_index=True)

    class Meta:
        abstract = True
        ordering = ['order']


class Visitor(models.Model):
    """访客"""

    visited = None
    visitor = None
    time_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-time_updated']


class Favorer(models.Model):
    """收藏"""

    favored = None
    favorer = None
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-time_created']
