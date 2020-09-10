#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

from . import EnabledManager


__all__ = ['ForumBoard', 'ForumPost']


class ForumBoard(models.Model):
    """板块"""

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    owner = models.ForeignKey(
        'User', models.CASCADE, 'forum_boards', default=None, null=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    is_system_board = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'forum_board'


class ForumPost(models.Model):
    """帖子"""

    board = models.ForeignKey('ForumBoard', models.CASCADE, 'posts')
    author = models.ForeignKey('User', models.CASCADE, '+')
    # if null, then it's the main post
    main_post = models.ForeignKey(
        'self', models.CASCADE, 'posts', default=None, null=True)

    title = models.CharField(max_length=20)
    content = models.CharField(max_length=300)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'forum_post'
        ordering = ['-time_created']
