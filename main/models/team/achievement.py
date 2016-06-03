from datetime import datetime
from django.db import models

from ChuangYi.settings import IMAGE_PATH
from main.models.mixins import PictureMixin


class TeamAchievementManager(models.Manager):
    def get_queryset(self):
        return super(TeamAchievementManager, self).get_queryset().filter(
            team__is_enabled=True)


class TeamAchievement(models.Model, PictureMixin):
    """
    团队成果
    """
    team = models.ForeignKey(
        'Team', models.CASCADE, 'achievements', verbose_name='团队')
    picture = models.ImageField('图片', db_index=True, upload_to=IMAGE_PATH)
    description = models.TextField(
        '成果描述', max_length=100, default='', db_index=True)
    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    enabled = TeamAchievementManager()

    class Meta:
        db_table = 'team_achievement'
        ordering = ['-create_time']