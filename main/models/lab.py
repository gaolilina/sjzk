from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment, Follower, Liker, Tag, \
    Visitor

__all__ = ['Lab', 'LabAchievement', 'LabComment', 'LabFollower', 'LabInvitation',
           'LabLiker', 'LabMember', 'LabMemberRequest', 'LabNeed',
           'LabTag', 'LabVisitor',  # 'InternalTask', 'ExternalTask',
           'LabFeature', 'LabScore', 'LabNeedFollower', 'LabTagLiker', 'LabAchievementLiker']


class Lab(models.Model):
    owner = models.ForeignKey('User', models.CASCADE, 'owned_labs')
    name = models.CharField(max_length=20)
    icon = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=100, default='')
    url = models.CharField(max_length=100)
    field1 = models.CharField(max_length=10, db_index=True, default='')
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
        db_table = 'lab'
        ordering = ['-time_created']


class LabAchievement(models.Model):
    """团队成果"""

    lab = models.ForeignKey('Lab', models.CASCADE, 'achievements')
    description = models.CharField(max_length=100, default='')
    picture = models.CharField(max_length=100, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'lab_achievement'
        ordering = ['-time_created']


class LabAchievementLiker(Liker):
    """团队动态点赞记录"""

    liked = models.ForeignKey('LabAchievement', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_lab_achievements')

    class Meta:
        db_table = 'lab_achievement_liker'


class LabComment(Comment):
    """团队评论"""

    entity = models.ForeignKey('lab', models.CASCADE, 'comments')

    class Meta:
        db_table = 'lab_comment'
        ordering = ['time_created']


class LabFollower(Follower):
    """团队关注记录"""

    followed = models.ForeignKey('Lab', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE, 'followed_labs')

    class Meta:
        db_table = 'lab_follower'


class LabInvitation(models.Model):
    """团队邀请"""

    lab = models.ForeignKey('Lab', models.CASCADE, 'invitations')
    user = models.ForeignKey('User', models.CASCADE, 'lab_invitations')
    description = models.CharField(max_length=100)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'lab_invitation'
        ordering = ['-time_created']


class LabLiker(Liker):
    """团队点赞记录"""

    liked = models.ForeignKey('Lab', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_labs')

    class Meta:
        db_table = 'lab_liker'


class LabMember(models.Model):
    """团队成员"""

    lab = models.ForeignKey('Lab', models.CASCADE, 'members')
    user = models.ForeignKey('User', models.CASCADE, 'labs')

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'lab_member'
        ordering = ['-time_created']


class LabMemberRequest(models.Model):
    """团队成员申请记录"""

    lab = models.ForeignKey('Lab', models.CASCADE, 'member_requests')
    user = models.ForeignKey('User', models.CASCADE, '+')
    description = models.TextField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'lab_member_request'
        ordering = ['-time_created']


class LabNeed(models.Model):
    """团队需求信息"""

    lab = models.ForeignKey('Lab', models.CASCADE, 'needs')
    # 0: member, 1: outsource, 2: undertake
    type = models.IntegerField(db_index=True)
    title = models.TextField(max_length=20)
    # 地区相关
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    county = models.CharField(max_length=20, default='')
    description = models.CharField(default='', max_length=200)
    # 0: pending, 1: completed, 2: removed
    status = models.IntegerField(default=0, db_index=True)
    number = models.IntegerField(default=None, null=True)
    field = models.CharField(default='', max_length=20)
    skill = models.CharField(default='', max_length=20)
    deadline = models.DateField(default=None, null=True, db_index=True)

    age_min = models.IntegerField(default=0)
    age_max = models.IntegerField(default=0)
    gender = models.IntegerField(default=0, db_index=True)
    degree = models.CharField(default='', max_length=20)
    major = models.CharField(default='', max_length=20)
    time_graduated = models.DateField(default=None, null=True)

    cost = models.IntegerField(default=0)
    cost_unit = models.CharField(default='', max_length=1)
    time_started = models.DateField(default=None, null=True)
    time_ended = models.DateField(default=None, null=True)
    # 成员或团队Id
    members = models.CharField(default='', max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'lab_need'
        ordering = ['-time_created']


class LabNeedFollower(Follower):
    """团队需求关注记录"""

    followed = models.ForeignKey('LabNeed', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE, 'lab_followed_needs')

    class Meta:
        db_table = 'lab_need_follower'


class LabTag(Tag):
    """团队标签"""

    entity = models.ForeignKey('Lab', models.CASCADE, 'tags')

    class Meta:
        db_table = 'lab_tag'


class LabVisitor(Visitor):
    """团队访客"""

    visited = models.ForeignKey('Lab', models.CASCADE, 'visitors')
    visitor = models.ForeignKey('User', models.CASCADE, 'visited_labs')

    class Meta:
        db_table = 'lab_visitor'


class LabScore(models.Model):
    """团队积分明细"""

    lab = models.ForeignKey('Lab', models.CASCADE, 'score_records')
    score = models.IntegerField(db_index=True)
    description = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=10, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'lab_score_record'


class LabFeature(models.Model):
    """团队特征模型"""

    lab = models.OneToOneField('Lab', models.CASCADE, related_name='feature_model')
    data = models.TextField(default="{}")

    class Meta:
        db_table = 'lab_feature'


class LabTagLiker(Liker):
    """团队标签点赞记录"""

    liked = models.ForeignKey('LabTag', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_lab_tags')

    class Meta:
        db_table = 'lab_tag_liker'
