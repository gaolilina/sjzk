from datetime import datetime
from django.db import models


class TeamMemberManager(models.Manager):
    def get_queryset(self):
        return super(TeamMemberManager, self).get_queryset().filter(
            team__is_enabled=True, member__is_enabled=True)


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

    enabled = TeamMemberManager()

    @classmethod
    def exist(cls, user, team):
        """
        检查user是否为团队成员

        """
        return cls.enabled.filter(member=user, team=team).exists()


class TeamMemberRequestManager(models.Manager):
    def get_queryset(self):
        return super(TeamMemberRequestManager, self).get_queryset().filter(
            sender__is_enabled=True, receiver__is_enabled=True)


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
        检查user是否向team发送过加入申请

        """
        return cls.enabled.filter(sender=sender, receiver=receiver).exists()


class TeamInvitationManager(models.Manager):
    def get_queryset(self):
        return super(TeamInvitationManager, self).get_queryset().filter(
            sender__is_enabled=True, receiver__is_enabled=True)


class TeamInvitation(models.Model):
    """
    团队邀请信息

    """
    sender = models.ForeignKey(
        'Team', models.CASCADE, 'invitations', verbose_name='邀请方')
    receiver = models.ForeignKey(
        'User', models.CASCADE, 'invitations', verbose_name='被邀请用户')

    description = models.TextField(
        '附带消息', max_length=100, db_index=True)
    is_read = models.BooleanField(
        '该邀请是否已读', default=False, db_index=True)

    create_time = models.DateTimeField(
        '邀请时间', default=datetime.now, db_index=True)

    enabled = TeamInvitationManager()

    class Meta:
        db_table = 'team_invitation'
        ordering = ['-create_time']

    @classmethod
    def exist(cls, sender, receiver):
        """
        检查team是否向user发送过加入邀请

        """
        return cls.enabled.filter(sender=sender, receiver=receiver).exists()