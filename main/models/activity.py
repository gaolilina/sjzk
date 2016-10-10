from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment


__all__ = ['Activity', 'ActivityUserParticipator', 'ActivityComment']


class Activity(models.Model):
    """活动基本信息"""

    name = models.CharField(max_length=50, db_index=True)
    content = models.CharField(max_length=1000)
    deadline = models.DateTimeField(db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    allow_user = models.BooleanField(default=True)
    allow_team = models.BooleanField(default=True)

    is_enabled = models.BooleanField(default=True)

    enabled = EnabledManager()

    class Meta:
        db_table = 'activity'
        ordering = ['-time_created']


class ActivityUserParticipator(models.Model):
    """活动参与者（用户）"""

    activity = models.ForeignKey('Activity', models.CASCADE, 'user_participators')
    user = models.ForeignKey('User', models.CASCADE, '+')

    class Meta:
        db_table = 'activity_user_participator'


class ActivityComment(Comment):
    """活动评论"""

    entity = models.ForeignKey('Activity', models.CASCADE, 'comments')

    class Meta:
        db_table = 'activity_comment'
