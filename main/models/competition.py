#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment, Liker, Follower, Favorer

__all__ = ['Competition', 'CompetitionStage', 'CompetitionTeamParticipator',
           'CompetitionComment', 'CompetitionLiker', 'CompetitionFile',
           'CompetitionNotification', 'CompetitionFollower', 'CompetitionAward',
           'CompetitionFavorer', 'CompetitionSign']


class CompetitionSign(models.Model):
    class Meta:
        db_table = 'competition_sign'

    competition = models.ForeignKey('Competition', related_name='signers')
    team = models.ForeignKey('Team', related_name='+')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)


class Competition(models.Model):
    """竞赛基本信息"""

    name = models.CharField(max_length=50, null=True)
    status = models.IntegerField(default=0, db_index=True)
    content = models.CharField(max_length=1000, null=True)
    deadline = models.DateTimeField(db_index=True, null=True)
    time_started = models.DateTimeField(db_index=True, null=True)
    time_ended = models.DateTimeField(db_index=True, null=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # 竞赛允许的团队上限，0：不限
    allow_team = models.IntegerField(default=0, db_index=True)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    min_member = models.IntegerField(default=1, db_index=True)
    max_member = models.IntegerField(default=1, db_index=True)
    unit = models.CharField(max_length=20, default='')
    # 领域
    field = models.CharField(max_length=20, default='')
    # 0:不限, 1:学生, 2:教师, 3:在职
    user_type = models.IntegerField(default=0, db_index=True)

    is_enabled = models.BooleanField(default=True)

    owner_user = models.ForeignKey('User', related_name='+', null=True)
    experts = models.ManyToManyField('User', related_name='scored_competitions')
    sponsor = models.ForeignKey('Lab', related_name='sponsored_competitions', null=True)
    # 费用二维码
    expense = models.CharField(max_length=100, default='')
    # 标签
    tags = models.CharField(max_length=255, default='')

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'competition'
        ordering = ['-time_created']


class CompetitionStage(models.Model):
    """竞赛阶段"""

    # 宣传
    STAGE_PROPAGANDA = 0
    # 报名
    STAGE_APPLY = 1
    # 结束
    STAGE_END = 100

    # 不是比赛中的阶段
    STAGES_ERROR = [STAGE_END, STAGE_APPLY, STAGE_PROPAGANDA]

    competition = models.ForeignKey('Competition', models.CASCADE, 'stages')
    status = models.IntegerField(default=0, db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'competition_stage'


class CompetitionNotification(models.Model):
    """竞赛通知"""

    competition = models.ForeignKey('Competition', models.CASCADE, 'notifications')
    status = models.IntegerField(default=0, db_index=True)
    notification = models.CharField(max_length=1000)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'competition_notification'


class CompetitionFile(models.Model):
    """竞赛文件"""

    competition = models.ForeignKey('Competition', models.CASCADE, 'team_files')
    team = models.ForeignKey('Team', models.CASCADE, 'competition_files')
    status = models.IntegerField(default=0, db_index=True)
    file = models.CharField(max_length=100, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    # 0:文档，1:视频，2:代码
    type = models.IntegerField(default=2)

    # 评分
    score = models.CharField(max_length=100, default='')
    comment = models.TextField(default='')

    objects = models.Manager()

    class Meta:
        db_table = 'competition_file'


class CompetitionTeamParticipator(models.Model):
    """竞赛参与者（团队）"""

    competition = models.ForeignKey('Competition', models.CASCADE, 'team_participators')
    team = models.ForeignKey('Team', models.CASCADE, 'competitions')
    rater = models.ForeignKey('User', related_name='rated_team_participators', null=True)
    score = models.IntegerField(default=0)
    # 表示是否终止，报名阶段均是未通过
    final = models.BooleanField(default=False)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'competition_team_participator'
        ordering = ['-time_created']


class CompetitionComment(Comment):
    """竞赛评论"""

    entity = models.ForeignKey('Competition', models.CASCADE, 'comments')

    class Meta:
        db_table = 'competition_comment'
        ordering = ['time_created']


class CompetitionLiker(Liker):
    """竞赛点赞记录"""

    liked = models.ForeignKey('Competition', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_competitions')

    class Meta:
        db_table = 'competition_liker'


class CompetitionFollower(Follower):
    """竞赛关注记录"""

    followed = models.ForeignKey('Competition', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE,
                                 'followed_competitions')

    class Meta:
        db_table = 'competition_follower'


class CompetitionAward(models.Model):
    """竞赛评比"""

    competition = models.ForeignKey('Competition', models.CASCADE, 'awards')
    team = models.ForeignKey('Team', models.CASCADE, 'awards')
    award = models.CharField(max_length=50)

    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'competition_award'
        ordering = ['-time_created']


class CompetitionFavorer(Favorer):
    """活动收藏记录"""

    favored = models.ForeignKey('Competition', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_competitions')

    class Meta:
        db_table = 'competition_favorer'
