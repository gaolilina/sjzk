from django.db import models

from team.models import Team
from user.models import User


class VisitorInfo(models.Model):
    visitor = None
    count = models.IntegerField('访问次数', default=0, db_index=True)
    last_visit_time = models.DateTimeField('最后一次访问时间', db_index=True)

    class Meta:
        abstract = True
        ordering = ['-last_visit_time']


class UserVisitor(VisitorInfo):
    """
    APP用户来访者记录

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'visitor_info', verbose_name='用户')
    visitor = models.ForeignKey(
        User, models.CASCADE, 'visited_user_info')

    class Meta:
        db_table = 'user_visitor'


class TeamVisitor(VisitorInfo):
    """
    团队来访者记录

    """
    team = models.ForeignKey(
        Team, models.CASCADE, 'visitor_info', verbose_name='团队')
    visitor = models.ForeignKey(
        User, models.CASCADE, 'visited_team_info')

    class Meta:
        db_table = 'team_visitor'
