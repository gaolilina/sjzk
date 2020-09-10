#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models

__all__ = ['CompetitionOwner']


class CompetitionOwner(models.Model):
    """竞赛创建者"""

    competition = models.ForeignKey('main.Competition', models.CASCADE, 'owner')
    user = models.ForeignKey('AdminUser', models.CASCADE, '+')

    class Meta:
        db_table = 'competition_owner'
