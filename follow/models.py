from django.db import models

from user.models import User
from team.models import Team


class FollowerInfo(models.Model):
    followed = None
    follower = None
    create_time = models.DateTimeField('关注时间', db_index=True)

    class Meta:
        abstract = True
        ordering = ['-create_time']


class UserFollower(FollowerInfo):
    """
    APP用户关注者记录

    """
    followed = models.ForeignKey(
        User, models.CASCADE, related_name='follower_info')
    follower = models.ForeignKey(
        User, models.CASCADE, related_name='followed_user_info')

    class Meta:
        db_table = 'user_follower'

    def __repr__(self):
        return '<User Follower - %s / %s>' % (
            self.followed.name, self.follower.name)


class TeamFollower(FollowerInfo):
    """
    团队关注者记录

    """
    followed = models.ForeignKey(
        Team, models.CASCADE, related_name='follower_info')
    follower = models.ForeignKey(
        User, models.CASCADE, related_name='followed_team_info')

    class Meta:
        db_table = 'team_follower'

    def __repr__(self):
        return '<Team Follower - %s / %s>' % (
            self.followed.name, self.follower.name)
