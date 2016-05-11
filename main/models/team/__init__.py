from datetime import datetime

from django.db import models

from main.models.mixins import IconMixin


class TeamManager(models.Manager):
    def get_queryset(self):
        return super(TeamManager, self).get_queryset().filter(
            is_enabled=True, owner__is_enabled=True)


class Team(models.Model, IconMixin):
    """
    团队基本信息

    """
    name = models.CharField(
        '名称', max_length=20, db_index=True)
    owner = models.ForeignKey(
        'User', models.CASCADE, 'owned_teams', verbose_name='创始人')
    members = models.ManyToManyField(
        'User', 'teams', through='TeamMember', verbose_name='成员')
    icon = models.ImageField(
        '图标', db_index=True)
    is_recruiting = models.BooleanField(
        '是否招募新成员', default=True, db_index=True)
    is_enabled = models.BooleanField(
        '是否有效', default=True)
    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    enabled = TeamManager()

    class Meta:
        db_table = 'team'


class TeamMember(models.Model):
    """
    团队成员记录

    """
    team = models.ForeignKey(
        'Team', models.CASCADE, 'member_records', verbose_name='团队')
    member = models.ForeignKey(
        'User', models.CASCADE, '+', verbose_name='成员')

    create_time = models.DateTimeField(
        '加入时间', default=datetime.now)


class TeamProfile(models.Model):
    team = models.ForeignKey(Team, models.CASCADE, 'profile')

    description = models.TextField(
        '团队简介', max_length=100, default='', db_index=True)
    # and other stuffs...

    class Meta:
        db_table = 'team_profile'
