import hashlib

from django.db import models
from django.utils import timezone

from ..models import EnabledManager, Comment, Follower, Liker, Tag,\
    Visitor, Favorer
from main.models.action import Action

__all__ = ['UserVote', 'UserVoteOption', 'UserVoteOptionAdvocator',
           'LabVote', 'LabVoteOption', 'LabVoteOptionAdvocator',]


class UserVote(models.Model):
    is_enabled = models.BooleanField(default=True, db_index=True)
    owner = models.ForeignKey('User', models.CASCADE, 'votes')
    content = models.TextField(default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    deadline = models.DateTimeField(null=True)
    is_closed = models.BooleanField(default=False)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'user_vote'
        ordering = ['-time_created']


class UserVoteOption(models.Model):
    entity = models.ForeignKey('UserVote', models.CASCADE, 'options')
    content = models.TextField(default='')

    class Meta:
        db_table = 'user_vote_option'


class UserVoteOptionAdvocator(models.Model):
    entity = models.ForeignKey('UserVoteOption', models.CASCADE, 'advocators')
    user = models.ForeignKey('User', models.CASCADE, '+')
    time_created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user_vote_option_advocator'
        ordering = ['-time_created']


class LabVote(models.Model):
    is_enabled = models.BooleanField(default=True, db_index=True)
    owner = models.ForeignKey('Lab', models.CASCADE, 'votes')
    content = models.TextField(default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    deadline = models.DateTimeField(null=True)
    is_closed = models.BooleanField(default=False)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'lab_vote'
        ordering = ['-time_created']


class LabVoteOption(models.Model):
    entity = models.ForeignKey('LabVote', models.CASCADE, 'options')
    content = models.TextField(default='')

    class Meta:
        db_table = 'lab_vote_option'


class LabVoteOptionAdvocator(models.Model):
    entity = models.ForeignKey('LabVoteOption', models.CASCADE, 'advocators')
    user = models.ForeignKey('User', models.CASCADE, '+')
    time_created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'lab_vote_option_advocator'
        ordering = ['-time_created']
