from django.db import models
from django.utils import timezone

from . import EnabledManager, Comment


__all__ = ['Competition', 'CompetitionTeamParticipator', 'CompetitionComment']


class Competition(models.Model):
    """竞赛基本信息"""

    name = models.CharField(max_length=50, db_index=True)
    content = models.CharField(max_length=1000)
    deadline = models.DateTimeField(db_index=True)
    time_started = models.DateTimeField(db_index=True)
    time_ended = models.DateTimeField(db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    allow_user = models.BooleanField(default=True)
    allow_team = models.BooleanField(default=True)

    is_enabled = models.BooleanField(default=True)

    enabled = EnabledManager()

    class Meta:
        db_table = 'competition'
        ordering = ['-time_created']


class CompetitionTeamParticipator(models.Model):
    """竞赛参与者（团队）"""

    competition = models.ForeignKey('Competition', models.CASCADE, 'team_participators')
    team = models.ForeignKey('Team', models.CASCADE, '+')

    class Meta:
        db_table = 'competition_team_participator'


class CompetitionComment(Comment):
    """竞赛评论"""

    entity = models.ForeignKey('Competition', models.CASCADE, 'comments')

    class Meta:
        db_table = 'competition_comment'
