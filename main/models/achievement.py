from django.db import models
from django.utils import timezone

from main.models import Liker

__all__ = ['UserAchievement', 'UserAchievementLiker', 'TeamAchievement']


class TeamAchievement(models.Model):
    """团队成果"""

    team = models.ForeignKey('Team', models.CASCADE, 'achievements')
    description = models.CharField(max_length=100, default='')
    picture = models.CharField(max_length=100, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_achievement'
        ordering = ['-time_created']


class UserAchievement(models.Model):
    """用户成果"""

    user = models.ForeignKey('User', models.CASCADE, 'achievements')
    description = models.CharField(max_length=100, default='')
    picture = models.CharField(max_length=255, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    requirers = models.ManyToManyField('User', related_name='requireAchievements')

    class Meta:
        db_table = 'user_achievement'
        ordering = ['-time_created']


class UserAchievementLiker(Liker):
    """成果点赞记录"""

    liked = models.ForeignKey('UserAchievement', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_user_achievements')

    class Meta:
        db_table = 'user_achievement_liker'
