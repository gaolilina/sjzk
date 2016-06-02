from django.db import models

from ChuangYi.settings import IMAGE_PATH


class TeamAchievement(models.Manager):
    """
    团队成果
    """
    team = models.ForeignKey(
        'Team', models.CASCADE, 'achievements', verbose_name='团队')
    picture = models.ImageField('图片', db_index=True, upload_to=IMAGE_PATH)
    description = models.TextField(
        '成果描述', max_length=100, default='', db_index=True)