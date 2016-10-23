from django.db import models
from django.utils import timezone


__all__ = ['Group', 'GroupMember', 'GroupMemberRequest', 'GroupInvitation']


class Group(models.Model):
    """群组模型"""

    owner = models.ForeignKey('User', models.CASCADE, 'owned_groups')
    name = models.CharField(max_length=20, db_index=True)
    is_enabled = models.BooleanField(default=True, db_index=True)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'group'
        ordering = ['-time_created']

        
class GroupMember(models.Model):
    """群组成员"""

    group = models.ForeignKey('Group', models.CASCADE, 'members')
    user = models.ForeignKey('User', models.CASCADE, 'groups')

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'group_member'
        ordering = ['-time_created']


class GroupMemberRequest(models.Model):
    """群组成员申请记录"""

    group = models.ForeignKey('Group', models.CASCADE, 'member_requests')
    user = models.ForeignKey('User', models.CASCADE, '+')
    description = models.TextField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'group_member_request'
        ordering = ['-time_created']
        

class GroupInvitation(models.Model):
    """群组邀请"""

    group = models.ForeignKey('Group', models.CASCADE, 'invitations')
    user = models.ForeignKey('User', models.CASCADE, 'group_invitations')
    description = models.CharField(max_length=100)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'group_invitation'
        ordering = ['-time_created']