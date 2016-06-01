from datetime import datetime

from django.db import models, transaction

from ChuangYi.settings import IMAGE_PATH
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
            team = cls(owner=user, name=name, **kwargs)
            team.save()
            TeamProfile.objects.create(team=team)
        return team


class TeamProfile(models.Model):
    team = models.OneToOneField(Team, models.CASCADE, related_name='profile')

    description = models.TextField(
        '团队简介', max_length=100, default='', db_index=True)
    url = models.URLField('团队链接', max_length=100, default='')
    field1 = models.CharField('团队领域1', max_length=10,
                              db_index=True, default='')
    field2 = models.CharField('团队领域2', max_length=10,
                              db_index=True, default='')

    class Meta:
        db_table = 'team_profile'

    @classmethod
    def get_fields(cls, team):
        """
        获取团队所属领域
        :param team: 团队
        :return: fields: 所属领域，格式：[field1, field2]
        """
        fields = list()
        if team.profile.field1:
            fields.append(team.profile.field1)
        else:
            fields.append(None)
        if team.profile.field2:
            fields.append(team.profile.field2)
        else:
            fields.append(None)
        return fields
