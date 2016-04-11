from django.db import models
from django.utils import timezone

from user.models import User


class Team(models.Model):
    """
    团队基本信息

    """
    name = models.CharField('名称', max_length=20, db_index=True)
    description = models.TextField('简介', max_length=100, db_index=True)
    owner = models.ForeignKey(
        User, models.CASCADE, 'owned_teams', 'owned_team',
        verbose_name='创始人')
    managers = models.ManyToManyField(
        User, 'managed_teams', 'managed_team',
        verbose_name='管理员', db_table='team_manager')
    members = models.ManyToManyField(
        User, 'teams', 'team',
        verbose_name='成员', through='TeamMembership')
    is_enabled = models.BooleanField('是否有效', default=True)

    class Meta:
        db_table = 'team'

    def __repr__(self):
        return '<Team - %s (%s)>' % (self.name, self.owner.name)


class TeamMembership(models.Model):
    """
    团队成员

    """
    team = models.ForeignKey(
        Team, models.CASCADE, 'membership', verbose_name='团队')
    member = models.ForeignKey(
        User, models.CASCADE, '+', verbose_name='成员')
    join_time = models.DateTimeField('加入时间', default=timezone.now)

    class Meta:
        db_table = 'team_member'

    def __repr__(self):
        return '<Team Membership - %s>' % self.team.name


class TeamProfile(models.Model):
    """
    团队基本资料

    """
    team = models.ForeignKey(Team, models.CASCADE, related_name='profile')

    description = models.TextField(
        '团队简介', max_length=100, default='', db_index=True)
    url = models.TextField(
        '相关链接', max_length=100, default='', db_index=True)
    is_recruiting = models.BooleanField(
        '是否招募新成员', default=True, db_index=True)
    icon = models.ImageField('团队图标')

    class Meta:
        db_table = 'team_profile'

    def __repr__(self):
        return '<Team Profile - %s>' % self.team.name
