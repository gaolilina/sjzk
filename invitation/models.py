from django.db import models

from team.models import Team
from user.models import User


class TeamInvitation(models.Model):
    """
    团队邀请信息

    """
    team = models.ForeignKey(
        Team, models.CASCADE, 'invitations', 'invitation',
        verbose_name='邀请方团队')
    user = models.ForeignKey(
        User, models.CASCADE, 'invitations', 'invitation',
        verbose_name='被邀请用户')
    description = models.TextField('附带消息', max_length=100, db_index=True)
    create_time = models.DateTimeField('邀请时间', db_index=True)
    is_read = models.BooleanField(
        '该邀请是否已读', default=False, db_index=True)
    is_ignored = models.BooleanField(
        '该邀请是否已被忽略', default=False, db_index=True)

    class Meta:
        db_table = 'team_invitation'
        ordering = ['-create_time']

    def __repr__(self):
        return '<Team Invitaion - %s / %s>' % (self.team.name, self.user.name)
