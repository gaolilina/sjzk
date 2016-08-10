from django.db import models
from django.utils import timezone

from . import EnabledManager, Action, Comment, Follower, Liker, Tag, Visitor


__all__ = ['Team', 'TeamAction', 'TeamAchievement', 'TeamComment',
           'TeamFollower', 'TeamInvitation', 'TeamLiker', 'TeamMember',
           'TeamMemberRequest', 'TeamNeed', 'TeamTag', 'TeamVisitor']


class Team(models.Model):
    """团队模型"""

    owner = models.ForeignKey('User', models.CASCADE, 'owned_teams')
    name = models.CharField(max_length=20, db_index=True)
    description = models.CharField(max_length=100, default='')
    url = models.CharField(max_length=100)
    field1 = models.CharField(max_length=10, db_index=True, default='')
    field2 = models.CharField(max_length=10, db_index=True, default='')
    province = models.CharField(max_length=20, default='', db_index=True)
    city = models.CharField(max_length=20, default='', db_index=True)
    county = models.CharField(max_length=20, default='', db_index=True)
    is_recruiting = models.BooleanField(default=True, db_index=True)
    is_enabled = models.BooleanField(default=True, db_index=True)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    enabled = EnabledManager()

    class Meta:
        db_table = 'team'
        ordering = ['-time_created']


class TeamAction(Action):
    """团队动态"""

    entity = models.ForeignKey('Team', models.CASCADE, 'actions')

    class Meta:
        db_table = 'team_action'


class TeamAchievement(models.Model):
    """团队成果"""

    team = models.ForeignKey('Team', models.CASCADE, 'achievements')
    description = models.CharField(max_length=100, default='')
    picture = models.CharField(max_length=100, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_achievement'
        ordering = ['-time_created']


class TeamComment(Comment):
    """团队评论"""

    entity = models.ForeignKey('team', models.CASCADE, 'comments')

    class Meta:
        db_table = 'team_comment'


class TeamFollower(Follower):
    """团队关注记录"""

    followed = models.ForeignKey('Team', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE, 'followed_teams')

    class Meta:
        db_table = 'team_follower'


class TeamInvitation(models.Model):
    """团队邀请"""

    team = models.ForeignKey('Team', models.CASCADE, 'invitations')
    user = models.ForeignKey('User', models.CASCADE, 'invitations')
    description = models.CharField(max_length=100)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_invitation'
        ordering = ['-time_created']


class TeamLiker(Liker):
    """团队点赞记录"""

    liked = models.ForeignKey('Team', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_teams')

    class Meta:
        db_table = 'team_liker'


class TeamMember(models.Model):
    """团队成员"""

    team = models.ForeignKey('Team', models.CASCADE, 'members')
    user = models.ForeignKey('User', models.CASCADE, 'teams')

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_member'
        ordering = ['-time_created']


class TeamMemberRequest(models.Model):
    """团队成员申请记录"""

    team = models.ForeignKey('Team', models.CASCADE, 'member_requests')
    user = models.ForeignKey('User', models.CASCADE, '+')
    description = models.TextField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_member_request'
        ordering = ['-time_created']


class TeamNeed(models.Model):
    """团队需求信息"""

    team = models.ForeignKey('Team', models.CASCADE, 'needs')
    # 0: member, 1: outsource, 2: undertake
    type = models.IntegerField(db_index=True)
    title = models.TextField(max_length=20)
    description = models.CharField(default='', max_length=200)
    # 0: pending, 1: completed, 2: removed
    status = models.IntegerField(default=0, db_index=True)
    number = models.IntegerField(default=None, null=True)
    field = models.CharField(default='', max_length=20)
    skill = models.CharField(default='', max_length=20)
    deadline = models.DateTimeField(default=None, null=True, db_index=True)

    age_min = models.IntegerField(default=0)
    age_max = models.IntegerField(default=0)
    gender = models.CharField(default='', max_length=1)
    degree = models.CharField(default='', max_length=20)
    major = models.CharField(default='', max_length=20)
    time_graduated = models.DateField(default=None, null=True)

    cost = models.IntegerField(default=0)
    cost_unit = models.CharField(default='', max_length=1)
    time_started = models.DateField(default=None, null=True)
    time_ended = models.DateField(default=None, null=True)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_need'
        ordering = ['-time_created']


class MemberNeedRequest(models.Model):
    """人员需求的申请加入记录"""

    need = models.ForeignKey('TeamNeed', models.CASCADE, 'member_requests')
    sender = models.ForeignKey('User', models.CASCADE, 'member_requests')
    description = models.TextField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'member_need_request'
        ordering = ['-time_created']


class NeedCooperationRequest(models.Model):
    """外包、承接需求的合作申请记录"""

    need = models.ForeignKey('TeamNeed', models.CASCADE, 'cooperation_requests')
    sender = models.ForeignKey('Team', models.CASCADE, 'cooperation_requests')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'need_cooperation_request'
        ordering = ['-time_created']


class NeedCooperationInvitation(models.Model):
    """外包、承接需求的合作邀请记录"""

    need = models.ForeignKey('TeamNeed', models.CASCADE,
                             'cooperation_invitations')
    invitee = models.ForeignKey('Team', models.CASCADE,
                                'cooperation_invitations')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'need_cooperation_invitation'
        ordering = ['-time_created']


class TeamTag(Tag):
    """团队标签"""

    entity = models.ForeignKey('Team', models.CASCADE, 'tags')

    class Meta:
        db_table = 'team_tag'


class TeamVisitor(Visitor):
    """团队访客"""

    visited = models.ForeignKey('Team', models.CASCADE, 'visitors')
    visitor = models.ForeignKey('User', models.CASCADE, 'visited_teams')

    class Meta:
        db_table = 'team_visitor'
