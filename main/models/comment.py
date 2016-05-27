from datetime import datetime

from django.db import models


class CommentManager(models.Manager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset().filter(
            author__is_enabled=True)


class Comment(models.Model):
    """
    评论

    """
    object = None
    author = models.ForeignKey('User', models.CASCADE, '+')
    content = models.CharField(max_length=100, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    enabled = CommentManager()

    class Meta:
        abstract = True
        ordering = ['-create_time']


class UserComment(Comment):
    """
    关于用户的评论

    """
    object = models.ForeignKey('User', models.CASCADE, 'comments')


class TeamComment(Comment):
    """
    关于团队的评论

    """
    object = models.ForeignKey('Team', models.CASCADE, 'comments')
