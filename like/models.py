from django.db import models
from django.utils import timezone

from user.models import User
from team.models import Team
from project.models import Project
from activity.models import Activity


class LikerInfo(models.Model):
    liked = None
    liker = None
    create_time = models.DateTimeField('点赞时间', default=timezone.now)

    class Meta:
        abstract = True
        ordering = ['-create_time']


class UserLiker(LikerInfo):
    """
    APP用户点赞者记录

    """
    liked = models.ForeignKey(
        User, models.CASCADE, related_name='liker_info')
    liker = models.ForeignKey(
        User, models.CASCADE, related_name='liked_user_info')

    class Meta:
        db_table = 'user_liker'

    def __repr__(self):
        return '<User Liker - %s / %s>' % (self.liked.name, self.liker.name)


class TeamLiker(LikerInfo):
    """
    团队点赞者记录

    """
    liked = models.ForeignKey(
        Team, models.CASCADE, related_name='liker_info')
    liker = models.ForeignKey(
        User, models.CASCADE, related_name='liked_team_info')

    class Meta:
        db_table = 'team_liker'

    def __repr__(self):
        return '<Team Liker - %s / %s>' % (self.liked.name, self.liker.name)


class ProjectLiker(LikerInfo):
    """
    项目点赞者记录

    """
    liked = models.ForeignKey(
        Project, models.CASCADE, related_name='liker_info')
    liker = models.ForeignKey(
        User, models.CASCADE, related_name='liked_project_info')

    class Meta:
        db_table = 'project_liker'

    def __repr__(self):
        return '<Project Liker - %s / %s>' % (self.liked.name, self.liker.name)


class ActivityLiker(LikerInfo):
    """
    动态点赞者记录

    """
    liked = models.ForeignKey(
        Activity, models.CASCADE, related_name='liker_info')
    liker = models.ForeignKey(
        User, models.CASCADE, related_name='liked_activity_info')

    class Meta:
        db_table = 'activity_liker'

    def __repr__(self):
        return '<Activity Liker - %s / %s>' % (self.liked.id, self.liker.name)
