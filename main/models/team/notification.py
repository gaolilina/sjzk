from django.db import models
from datetime import datetime


class TeamNotification(models.Model):
    """
    系统通知

    """

    sender = models.CharField(
        '发送方名称', max_length=20, db_index=True)
    receivers = models.ManyToManyField(
        'Team', '+', through='NotificationReceipt')
    content = models.TextField(
        '内容', max_length=256, db_index=True)
    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)

    class Meta:
        db_table = 'team_notification'
        ordering = ['-create_time']


class TeamNotificationReceiptManager(models.Manager):
    def get_queryset(self):
        return super(TeamNotificationReceiptManager, self).get_queryset(
        ).filter(is_enabled=True)


class TeamNotificationReceipt(models.Model):
    """
    通知接收凭据

    """
    notification = models.ForeignKey(TeamNotification, models.CASCADE, '+')
    receiver = models.ForeignKey('Team', models.CASCADE, 'notifications')
    is_read = models.BooleanField(default=False, db_index=True)
    is_enabled = models.BooleanField(default=False, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    enabled = TeamNotificationReceiptManager()

    class Meta:
        db_table = 'team_notification_receiver'
        ordering = ['-create_time']

    @property
    def sender(self):
        return self.notification.sender

    @property
    def content(self):
        return self.notification.content
