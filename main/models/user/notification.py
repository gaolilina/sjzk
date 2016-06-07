from django.db import models
from datetime import datetime


class Notification(models.Model):
    """
    系统通知

    """

    sender = models.CharField(
        '发送方名称', max_length=20, db_index=True)
    receivers = models.ManyToManyField(
        'User', '+', through='NotificationReceipt')
    content = models.TextField(
        '内容', max_length=256, db_index=True)
    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-create_time']


class NotificationReceiptManager(models.Manager):
    def get_queryset(self):
        return super(NotificationReceiptManager, self).get_queryset().filter(
            is_enabled=True)


class NotificationReceipt(models.Model):
    """
    通知接收凭据

    """
    notification = models.ForeignKey(Notification, models.CASCADE, '+')
    receiver = models.ForeignKey('User', models.CASCADE, 'notifications')
    is_read = models.BooleanField(default=False, db_index=True)
    is_enabled = models.BooleanField(default=False, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    enabled = NotificationReceiptManager()

    class Meta:
        db_table = 'notification_receiver'
        ordering = ['-create_time']

    @property
    def sender(self):
        return self.notification.sender

    @property
    def content(self):
        return self.notification.content
