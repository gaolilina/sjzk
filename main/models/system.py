from django.db import models
from django.utils import timezone

from . import Liker, Comment, Favorer
from main.models.action import Action

__all__ = ['System', 'IllegalWord', 'SystemAction', 'SystemActionLiker',
           'SystemActionComment', 'SystemActionFavorer', 'SystemNotification',
           'SystemNotificationRecord']


class System(models.Model):
    """系统设定量"""

    # 版本号
    VERSION_NUMBER = models.FloatField(default=1.0)
    # 积分分值1
    SCORE_VALUE_ONE = models.IntegerField(default=10)
    # 积分分值2
    SCORE_VALUE_TWO = models.IntegerField(default=20)
    # 积分分值3
    SCORE_VALUE_THREE = models.IntegerField(default=50)
    # 积分分值4
    SCORE_VALUE_FOUR = models.IntegerField(default=100)
    # 积分分值5
    SCORE_VALUE_FIVE = models.IntegerField(default=200)
    # 举报封号次数阈值
    MAX_REPORTED = models.IntegerField(default=10)
    # 上传图片的最大数量
    pic_max = models.IntegerField(default=3)
    # 发布需求和成果最小的时间间隔，单位分钟
    publish_min_minute = models.IntegerField(default=60)
    # 最近访客的时间间隔，单位小时
    visit_max_hour = models.IntegerField(default=72)

    class Meta:
        db_table = 'system'


class IllegalWord(models.Model):
    """系统过滤词"""

    # 非法词汇
    word = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'illegal_word'


class SystemAction(Action):
    """系统动态"""

    entity = models.CharField(max_length=10, default='system')

    class Meta:
        db_table = 'system_action'


class SystemActionLiker(Liker):
    """系统动态点赞记录"""

    liked = models.ForeignKey('SystemAction', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_system_actions')

    class Meta:
        db_table = 'system_action_liker'


class SystemActionComment(Comment):
    """系统动态评论记录"""

    entity = models.ForeignKey('SystemAction', models.CASCADE, 'comments')

    class Meta:
        db_table = 'system_action_comment'


class SystemActionFavorer(Favorer):
    """系统动态收藏记录"""

    favored = models.ForeignKey('SystemAction', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_system_actions')

    class Meta:
        db_table = 'system_action_favorer'


class SystemNotification(models.Model):
    """系统通知"""

    content = models.CharField(max_length=500)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'system_notification'
        ordering = ['-time_created']


class SystemNotificationRecord(models.Model):
    """系统通知未读记录"""

    last_id = models.IntegerField(default=0)
    user = models.ForeignKey('User', models.CASCADE, 'system_notification_record')

    class Meta:
        db_table = 'system_notification_record'
