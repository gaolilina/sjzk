from django.db import models
from django.contrib.postgres.fields import JSONField

from team.models import Team


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
