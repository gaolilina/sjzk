from django.db import models
from django.utils import timezone


class LikerManager(models.Manager):
    def get_queryset(self):
        return super(LikerManager, self).get_queryset().filter(
            liked__is_enabled=True, liker__is_enabled=True)


class Liker(models.Model):
    liked = None
    liker = None
    create_time = models.DateTimeField(
        '点赞时间', default=timezone.now, db_index=True)

    enabled = LikerManager()

    class Meta:
        abstract = True
        ordering = ['-create_time']


class UserLiker(Liker):
    """
    用户点赞记录

    """
    liked = models.ForeignKey('User', models.CASCADE, 'liker_records')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_user_records')

    class Meta:
        db_table = 'user_liker'


class TeamLiker(Liker):
    """
    团队点赞记录

    """
    liked = models.ForeignKey('Team', models.CASCADE, 'liker_records')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_team_records')

    class Meta:
        db_table = 'team_liker'
