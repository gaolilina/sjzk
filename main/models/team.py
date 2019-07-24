from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment, Follower, Liker, Tag, \
    Visitor

__all__ = ['Team', 'TeamComment', 'TeamFollower', 'TeamInvitation',
           'TeamLiker', 'TeamMember', 'TeamMemberRequest', 'TeamTag', 'TeamVisitor', 'TeamFeature', 'TeamScore', 'TeamTagLiker']


class Team(models.Model):
    """团队模型"""

    owner = models.ForeignKey('User', models.CASCADE, 'owned_teams')
    name = models.CharField(max_length=20)
    icon = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=100, default='')
    url = models.CharField(max_length=100)
    # 领域
    field1 = models.CharField(max_length=10, db_index=True, default='')
    # field2 字段弃用
    field2 = models.CharField(max_length=10, db_index=True, default='')
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    county = models.CharField(max_length=20, default='')
    advantage = models.CharField(max_length=100, default='')
    # 工商阶段：0:未注册、1:注册未满3年、2:注册3年以上
    business_stage = models.IntegerField(default=0)
    # 融资阶段：等待投资、天使、A轮、B轮、C轮、D轮、E轮、F轮
    financing_stage = models.CharField(max_length=10, default='')
    # 团队估值
    valuation = models.IntegerField(default=0)
    # 团队估值单位
    valuation_unit = models.CharField(max_length=5, default='')
    is_recruiting = models.BooleanField(default=True, db_index=True)
    is_enabled = models.BooleanField(default=True, db_index=True)

    # 团队积分
    score = models.IntegerField(default=50, db_index=True)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'team'
        ordering = ['-time_created']


class TeamComment(Comment):
    """团队评论"""

    entity = models.ForeignKey('team', models.CASCADE, 'comments')

    class Meta:
        db_table = 'team_comment'
        ordering = ['time_created']


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


class TeamScore(models.Model):
    """团队积分明细"""

    team = models.ForeignKey('Team', models.CASCADE, 'score_records')
    score = models.IntegerField(db_index=True)
    description = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=10, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'team_score_record'


class TeamFeature(models.Model):
    """团队特征模型"""

    team = models.OneToOneField('Team', models.CASCADE,
                                related_name='feature_model')
    data = models.TextField(default="{}")

    class Meta:
        db_table = 'team_feature'


class TeamTagLiker(Liker):
    """团队标签点赞记录"""

    liked = models.ForeignKey('TeamTag', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_team_tags')

    class Meta:
        db_table = 'team_tag_liker'
