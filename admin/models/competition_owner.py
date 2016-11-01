from django.db import models

__all__ = ['CompetitionyOwner']


class CompetitionyOwner(models.Model):
    """竞赛管理者"""

    competition = models.ForeignKey('main.Competition', models.CASCADE, 'owner')
    user = models.ForeignKey('AdminUser', models.CASCADE, '+')

    class Meta:
        db_table = 'competition_owner'
