from datetime import datetime

from django.db import models


class EnabledBoardManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_enabled=True)


class UserBoardManager(EnabledBoardManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_system_board=False)


class SystemBoardManager(EnabledBoardManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_system_board=True)


class Board(models.Model):
    """板块"""

    name = models.CharField(
        '名称', max_length=20, db_index=True)
    description = models.CharField(
        '简介', max_length=50, db_index=True)
    owner = models.ForeignKey(
        'User', related_name='owned_board', verbose_name='版主')
    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)
    update_time = models.DateTimeField(
        '更新时间', default=datetime.now, db_index=True)
    is_system_board = models.BooleanField(
        '系统板块？', default=False)
    is_enabled = models.BooleanField(
        '有效？', default=True)

    enabled = EnabledBoardManager()
    from_user = UserBoardManager()
    from_system = SystemBoardManager()

    class Meta:
        db_table = 'forum_board'


class EnabledPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_enabled=True)


class MainPostManager(EnabledPostManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_main_post=True)


class Post(models.Model):
    """帖子"""

    author = models.ForeignKey('User', related_name='posts')  # 作者
    board = models.ForeignKey('Board', related_name='posts')  # 所属板块
    # parent = models.ForeignKey('Post', related_name='children')  # 楼主、层主的帖子

    content = models.CharField(
        '内容', max_length=250, db_index=True)
    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)
    is_main_post = models.BooleanField(
        '主题帖？')
    is_fixed = models.BooleanField(
        '置顶帖？', default=False)
    is_enabled = models.BooleanField(
        '有效？', default=True)

    enabled = EnabledPostManager()
    main = MainPostManager()

    class Meta:
        db_table = 'forum_post'
        ordering = ['-create_time']
