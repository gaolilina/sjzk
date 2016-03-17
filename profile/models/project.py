from django.db import models
from django.contrib.postgres.fields import JSONField

from project.models import Project


class ProjectProfile(models.Model):
    """
    项目基本资料

    """
    project = models.ForeignKey(Project, models.CASCADE, related_name='profile')

    description = models.TextField(
        '项目简介', max_length=100, default='', db_index=True)
    url = models.TextField(
        '相关链接', max_length=100, default='', db_index=True)
    status = models.IntegerField(
        '状态', default=0,
        choices=(('进行中', 0), ('已完成', 1), ('已取消', 2)))
    is_recruiting = models.BooleanField(
        '是否招募新成员', default=True, db_index=True)
    icon = models.ImageField('项目图标')

    class Meta:
        db_table = 'project_profile'

    def __repr__(self):
        return '<Project Profile - %s>' % self.project.name
