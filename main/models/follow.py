from datetime import datetime

from django.db import models


class FollowerManager(models.Manager):
    def get_queryset(self):
        return super(FollowerManager, self).get_queryset().filter(
            followed__is_enabled=True, follower__is_enabled=True)

    def exist(self, followed, follower):
        """
        判断用户之间是否有关注关系

        """
        return self.filter(followed=followed, follower=follower).exists()


class Follower(models.Model):
    """
    关注记录基类

    """
    followed = None
    follower = None
    create_time = models.DateTimeField(
        '关注时间', default=datetime.now, db_index=True)

    enabled = FollowerManager()

    class Meta:
        abstract = True
        ordering = ['-create_time']


class UserFollower(Follower):
    """
    用户的关注者记录

    """
    followed = models.ForeignKey(
        'User', models.CASCADE, 'follower_records')
    follower = models.ForeignKey(
        'User', models.CASCADE, 'followed_user_records')

    class Meta:
        db_table = 'user_follower'


class TeamFollower(Follower):
    """
    团队的关注者记录

    """
    followed = models.ForeignKey('Team', models.CASCADE, 'follower_records')
    follower = models.ForeignKey('User', models.CASCADE, 'followed_team_records')

    class Meta:
        db_table = 'team_follower'
