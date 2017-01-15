from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment, Liker


__all__ = ['Activity', 'ActivityStage','ActivityUserParticipator',
           'ActivityComment', 'ActivityLiker']


class Activity(models.Model):
    """活动基本信息"""

    name = models.CharField(max_length=50)
    content = models.CharField(max_length=1000)
    deadline = models.DateTimeField(db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # 活动允许的人数上限，0：不限
    allow_user = models.IntegerField(default=0, db_index=True)

    is_enabled = models.BooleanField(default=True)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'activity'
        ordering = ['-time_created']


class ActivityStage(models.Model):
    """活动阶段"""

    activity = models.ForeignKey('Activity', models.CASCADE, 'stages')
    # 0:前期宣传, 1:报名, 2:结束
    status = models.IntegerField(default=0, db_index=True)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    school = models.CharField(max_length=20, default='')
    # 0:不限, 1:学生, 2:教师, 3:社会人员
    user_type = models.IntegerField(default=0, db_index=True)

    class Meta:
        db_table = 'activity_stage'


class ActivityUserParticipator(models.Model):
    """活动参与者（用户）"""

    activity = models.ForeignKey(
        'Activity', models.CASCADE, 'user_participators')
    user = models.ForeignKey('User', models.CASCADE, '+')

    class Meta:
        db_table = 'activity_user_participator'


class ActivityComment(Comment):
    """活动评论"""

    entity = models.ForeignKey('Activity', models.CASCADE, 'comments')

    class Meta:
        db_table = 'activity_comment'


class ActivityLiker(Liker):
    """活动点赞记录"""

    liked = models.ForeignKey('Activity', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_activities')

    class Meta:
        db_table = 'activity_liker'
