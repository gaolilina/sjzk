from datetime import datetime

from django.db import models


class VisitorManager(models.Manager):
    def get_queryset(self):
        return super(VisitorManager, self).get_queryset().filter(
            visited__is_enabled=True, visitor__is_enabled=True)


class Visitor(models.Model):
    """
    访客记录基类

    """
    visited = None
    visitor = None
    count = models.IntegerField('访问计数', default=0, db_index=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, db_index=True)

    enabled = VisitorManager()

    class Meta:
        abstract = True
        ordering = ['-update_time']

    @staticmethod
    def update(visited, visitor):
        """
        更新对象的访客记录

        :param visited: 被访问对象
        :param visitor: 来访用户

        """
        now = datetime.now()
        record, created = visited.visitors.get_or_create(
            visitor=visitor, defaults={'count': 1})

        if not created:  # 同日内同一访客多次访问不更新访问计数
            if now.date() != record.update_time.date():
                record.count += 1
            record.save()


class UserVisitor(Visitor):
    """
    用户访客记录

    """
    visited = models.ForeignKey(
        'User', models.CASCADE, 'visitors', 'visitor')
    visitor = models.ForeignKey(
        'User', models.CASCADE, 'visited_users', 'visited_user')

    class Meta:
        db_table = 'user_visitor'
