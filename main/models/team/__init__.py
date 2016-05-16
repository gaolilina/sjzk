from datetime import datetime

from django.db import models, transaction

from ChuangYi.settings import IMAGE_PATH
from main.models.mixins import IconMixin
from main.models.user import User,UserToken


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
        '图标', db_index=True, upload_to=IMAGE_PATH)
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

    @classmethod
    def create(cls, user, name, **kwargs):
        """
        建立团队模型与其他相关模型

        :param name: 团队名
        :param kwargs: 其他团队模型相关的关键字参数

        """
        with transaction.atomic():
            description = ''
            if 'description' in kwargs:
                description = kwargs['description']
                kwargs.pop('description')
            team = cls(owner=user, name=name, **kwargs)
            team.save()
            if description.strip() != '':
                profile = TeamProfile(team=team)
                profile.description = description
                profile.save(update_fields=['description'])
        return team

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
