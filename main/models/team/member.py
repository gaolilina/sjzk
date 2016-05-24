from datetime import datetime
from django.db import models


class TeamMemberRequestManager(models.Manager):
    def get_queryset(self):
        return super(TeamMemberRequestManager, self).get_queryset().filter(
            sender__is_enabled=True, receiver__is_enabled=True)


class TeamMember(models.Model):
    """
    团队成员记录

    """
    team = models.ForeignKey(
        'Team', models.CASCADE, 'member_records', verbose_name='团队')
    member = models.ForeignKey(
        'User', models.CASCADE, '+', verbose_name='成员')

    create_time = models.DateTimeField(
        '加入时间', default=datetime.now)


class TeamMemberRequest(models.Model):
    """
    团队成员申请记录

    """
    sender = models.ForeignKey('User', models.CASCADE, '+')
    receiver = models.ForeignKey('Team', models.CASCADE, 'member_requests')

    description = models.TextField(
        '附带消息', max_length=100, db_index=True)
    create_time = models.DateTimeField(
        '申请时间', default=datetime.now, db_index=True)
    is_read = models.BooleanField(
        '该申请是否已读', default=False, db_index=True)

    enabled = TeamMemberRequestManager()

    class Meta:
        db_table = 'team_member_request'
        ordering = ['-create_time']

    @classmethod
    def exist(cls, sender, receiver):
        """
        检查user是否向other_user发送过好友请求

        """
        return cls.enabled.filter(sender=sender, receiver=receiver).exists()