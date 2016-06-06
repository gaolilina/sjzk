from datetime import datetime

from django.db import models


class TeamNeedManager(models.Manager):
    def get_queryset(self):
        return super(TeamNeedManager, self).get_queryset().filter(
            team__is_enabled=True)


class TeamNeed(models.Model):
    """
    团队需求信息

    """
    team = models.ForeignKey('Team', models.CASCADE, 'needs')

    description = models.TextField(
            '需求描述', max_length=100, db_index=True)
    status = models.IntegerField(
            '状态', default=0, choices=(('未满足', 0), ('已满足', 1)))
    number = models.IntegerField(
            '需求人数', default=-1, db_index=True)
    gender = models.IntegerField(
            '性别要求', default=0, choices=(('不限', 0), ('男', 1), ('女', 2)))

    create_time = models.DateTimeField(
            '创建时间', default=datetime.now, db_index=True)
    deadline = models.DateTimeField(
        '截止时间', default=None, blank=True, null=True, db_index=True)
    update_time = models.DateTimeField(
            '更新时间', auto_now=True, db_index=True)

    enabled = TeamNeedManager()

    class Meta:
        db_table = 'team_need'
        ordering = ['-create_time']
