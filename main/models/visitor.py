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
        record, created = visited.visitors.get_or_create(visitor=visitor)

        # 更新已有记录的访问时间
        if not created:
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
