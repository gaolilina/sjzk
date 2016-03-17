from django.db import models
from django.utils import timezone

from location.models import Province, City
from team.models import Team


class TeamNeed(models.Model):
    """
    团队需求信息

    """
    team = models.ForeignKey(Team, models.CASCADE, 'needs', 'need')
    description = models.TextField('需求描述', max_length=100, db_index=True)
    status = models.IntegerField(
        '状态', default=0, choices=(('未满足', 0), ('已满足', 1)))
    create_time = models.DateTimeField(
        '创建时间', default=timezone.now, db_index=True)
    number = models.IntegerField('需求人数', default=-1, db_index=True)
    gender = models.IntegerField(
        '性别要求', default=0, choices=(('不限', 0), ('男', 1), ('女', 2)))
    province = models.ForeignKey(
        Province, models.CASCADE, '+',
        verbose_name='地区要求（省级）',
        default=None, blank=True, null=True)
    city = models.ForeignKey(
        City, models.CASCADE, '+',
        verbose_name='地区要求（市级）',
        default=None, blank=True, null=True)

    class Meta:
        db_table = 'team_need'
        ordering = ['-create_time']

    def __repr__(self):
        return '<Team Need - %s (%s)>' % (self.id, self.team.name)
