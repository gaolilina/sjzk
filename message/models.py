from django.db import models
from django.utils import timezone

from team.models import Team
from user.models import User


class Message(models.Model):
    """
    短消息

    """
    sender = models.ForeignKey(
        User, models.CASCADE,
        verbose_name='发送方',
        related_name='messages_send', related_query_name='message_send')
    receiver = models.ForeignKey(
        User, models.CASCADE,
        verbose_name='接收方',
        related_name='messages_received', related_query_name='message_received')
    team = models.ForeignKey(
        Team, models.CASCADE, default=None, blank=True, null=True,
        verbose_name='发送方团队',
        related_name='messages_send', related_query_name='message_send')
    content = models.TextField('内容', max_length=100, db_index=True)
    create_time = models.DateTimeField(
        '创建时间', default=timezone.now, db_index=True)
    is_read = models.BooleanField(
        '接收方是否已读', default=False, db_index=True)
    is_hidden_from_sender = models.BooleanField(
        '发送方是否隐藏（删除）该消息', default=False, db_index=True)
    is_hidden_from_receiver = models.BooleanField(
        '接收方是否隐藏（删除）该消息', default=False, db_index=True)

    class Meta:
        db_table = 'message'
        ordering = ['-create_time']

    def __repr__(self):
        if self.team is not None:
            return '<Team Message - from: %s, to: %s>' % (
                self.team.name, self.receiver.name)
        else:
            return '<User Message - from: %s, to: %s>' % (
                self.sender.name, self.receiver.name)
