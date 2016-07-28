from django.db import models
from django.utils import timezone


__all__ = ['Action', 'Comment', 'Follower', 'Liker', 'Notification', 'Tag',
           'Visitor']


class Action(models.Model):
    """动态"""

    entity = None
    action = models.CharField(max_length=20)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    object_type = models.CharField(max_length=20)
    object_id = models.IntegerField(db_index=True)
    related_object_type = models.CharField(
        default=None, null=True, max_length=20)
    related_object_id = models.IntegerField(
        default=None, null=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-time_created']


class Comment(models.Model):
    """评论"""

    entity = None
    author = models.ForeignKey('User', models.CASCADE, '+')
    content = models.CharField(max_length=100, db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

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


class Notification(models.Model):
    """系统通知"""

    # if null, then it's a system notification
    team = models.ForeignKey('Team', models.CASCADE, 'notifications',
                             null=True, default=None)
    content = models.CharField(max_length=200, db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-time_created']


class Tag(models.Model):
    """标签记录"""

    entity = None
    name = models.CharField(max_length=20, db_index=True)
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