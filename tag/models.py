from django.db import models

from user.models import User
# from team.models import Team
# from activity.models import Activity


class Tag(models.Model):
    """
    标签索引

    """
    name = models.CharField('名称', max_length=10, unique=True, db_index=True)
    users = models.ManyToManyField(User, '+', through='UserTag')
    # teams = models.ManyToManyField(Team, '+', through='TeamTag')
    # activities = models.ManyToManyField(Activity, '+', through='ActivityTag')

    class Meta:
        db_table = 'tag'

    def __repr__(self):
        return '<Tag - %s>' % self.name


class TagInfo(models.Model):
    tag = models.ForeignKey(
        Tag, models.CASCADE, verbose_name='标签', related_name='+')
    order = models.IntegerField('序号')

    class Meta:
        abstract = True
        ordering = ['order']


class UserTag(TagInfo):
    """
    用户标签

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'tag_info', verbose_name='用户')

    class Meta:
        db_table = 'user_tag'


# class TeamTag(TagInfo):
#     """
#     团队标签
#
#     """
#     team = models.ForeignKey(
#         Team, models.CASCADE, 'tag_info', verbose_name='团队')
#
#     class Meta:
#         db_table = 'team_tag'
#
#
# class ActivityTag(TagInfo):
#     """
#     动态标签
#
#     """
#     activity = models.ForeignKey(
#         Activity, models.CASCADE, 'tag_info', verbose_name='动态')
#
#     class Meta:
#         db_table = 'activity_tag'
