from django.db import models
from django.utils import timezone

from user.models import User


class Notification(models.Model):
    """
    通知

    """

    sender = models.CharField('发送方名称', max_length=20, db_index=True)
    receivers = models.ManyToManyField(
        User, verbose_name='接收方', through='NotificationReceiver',
        related_name='+',
    )
    content = models.TextField('内容', max_length=100, db_index=True)
    create_time = models.DateTimeField(
        '创建时间', default=timezone.now, db_index=True
    )

    class Meta:
        db_table = 'notification'
        ordering = ['-create_time']

    def __repr__(self):
        return '<Notification - %s>' % self.id


class NotificationReceiver(models.Model):
    """
    通知接受者信息

    """
    notification = models.ForeignKey(Notification, models.CASCADE, '+')
    receiver = models.ForeignKey(User, models.CASCADE, 'notification_info')
    is_read = models.BooleanField(
        '接收方是否已读', default=False, db_index=True)
    is_hidden = models.BooleanField(
        '接收方是否隐藏（删除）该通知', default=False, db_index=True)

    class Meta:
        db_table = 'notification_receiver'
