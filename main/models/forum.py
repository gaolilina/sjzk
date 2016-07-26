from django.db import models
from django.utils import timezone

from . import EnabledManager


__all__ = ['ForumBoard']


class ForumBoard(models.Model):
    """板块"""

    name = models.CharField(max_length=20, db_index=True)
    description = models.CharField(max_length=100)
    manager = models.ForeignKey('User', models.CASCADE, 'forum_boards')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    is_system_board = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)

    enabled = EnabledManager()

    class Meta:
        db_table = 'forum_board'


class ForumPost(models.Model):
    """帖子"""

    board = models.ForeignKey('Board', models.CASCADE, 'posts')
    author = models.ForeignKey('User', models.CASCADE, '+')
    # if null, then it's the main post
    main_post = models.ForeignKey('self', models.CASCADE, 'posts',
                                  default=None, null=True)

    title = models.CharField(max_length=20)
    content = models.CharField(max_length=300)
    is_fixed = models.BooleanField(default=False, db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'forum_post'
        ordering = ['-create_time']
