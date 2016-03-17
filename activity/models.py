from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from user.models import User
from team.models import Team
from project.models import Project


class Activity(models.Model):
    """
    APP用户/团队/项目所发动态

    """
    author = models.ForeignKey(
        User, models.CASCADE, 'activities', 'activity',
        verbose_name='作者')
    team = models.ForeignKey(
        Team, models.CASCADE, 'activities', 'activity',
        verbose_name='所属团队', blank=True, default=None)
    project = models.ForeignKey(
        Project, models.CASCADE, 'activities', 'activity',
        verbose_name='所属项目', blank=True, default=None)
    content = models.TextField('内容', max_length=200, db_index=True)
    create_time = models.DateTimeField(
        '发布时间', default=timezone.now, db_index=True)
    modify_time = models.DateTimeField(
        '修改时间', blank=True, default=None, db_index=True)
    images = ArrayField(models.ImageField(), verbose_name='图片附件')

    class Meta:
        db_table = 'activity'
        ordering = ['-create_time']

    def __repr__(self):
        if self.project is not None:
            return '<Project Activity - %s (%s)>' % (self.project.name, self.id)
        elif self.team is not None:
            return '<Team Activity - %s (%s)>' % (self.team.name, self.id)
        else:
            return '<User Activity - %s (%s)>' % (self.author.name, self.id)
