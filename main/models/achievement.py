from django.db import models
from django.utils import timezone

__all__ = ['Achievement']


class Achievement(models.Model):
    """用户成果"""

    user = models.ForeignKey('User', models.CASCADE, 'achievements', default=None)
    # 用 team 是否为 None 区分团队成果或用户成果
    team = models.ForeignKey('Team', models.CASCADE, 'achievements', default=None, null=True)
    description = models.CharField(max_length=100, default='')
    picture = models.CharField(max_length=255, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    requirers = models.ManyToManyField('User', related_name='requireAchievements')
    likers = models.ManyToManyField('User', related_name='likeAchievements')

    class Meta:
        db_table = 'achievement'
        ordering = ['-time_created']
