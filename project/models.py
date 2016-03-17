from django.db import models
from django.utils import timezone

from team.models import Team
from user.models import User


class Project(models.Model):
    """
    项目基本信息

    """
    name = models.CharField('名称', max_length=20, db_index=True)
    description = models.TextField('简介', max_length=100, db_index=True)
    team = models.ForeignKey(
        Team, models.CASCADE, 'projects', 'project', verbose_name='所属团队')
    manager = models.ForeignKey(
        User, models.CASCADE, 'managed_projects', 'managed_project',
        verbose_name='负责人')
    members = models.ManyToManyField(
        User, 'projects', 'project',
        verbose_name='成员', through='ProjectMembership')
    is_enabled = models.BooleanField('是否有效', default=True)

    class Meta:
        db_table = 'project'

    def __repr__(self):
        return '<Project - %s (%s)>' % (self.name, self.team.name)


class ProjectMembership(models.Model):
    """
    项目成员

    """
    project = models.ForeignKey(
        Project, models.CASCADE, 'membership', verbose_name='项目')
    member = models.ForeignKey(
        User, models.CASCADE, '+', verbose_name='成员')
    join_time = models.DateTimeField('加入时间', default=timezone.now)

    class Meta:
        db_table = 'project_member'

    def __repr__(self):
        return '<Project Membership - %s>' % self.project.name
