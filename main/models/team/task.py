from datetime import datetime

from django.db import models


class TeamTaskManager(models.Manager):
    def get_queryset(self):
        return super(TeamTaskManager, self).get_queryset().filter(
            team__is_enabled=True)


class TeamTask(models.Model):
    """
    团队任务

    """
    team = models.ForeignKey('Team', models.CASCADE, 'tasks')

    name = models.CharField(
        '任务名称', max_length=20, db_index=True)
    description = models.TextField(
        '任务描述', max_length=100, db_index=True)
    status = models.IntegerField(
        '任务状态', default=0, db_index=True,
        choices=(('未完成', 0), ('已完成', 1),
                 ('已取消', 2), ('全部标记完成', 3)))
    expected_time = models.DateTimeField(
        '预期完成时间', default=None, blank=True, null=True, db_index=True)
    finish_time = models.DateTimeField(
        '实际完成时间', default=None, blank=True, null=True, db_index=True)
    executors = models.ManyToManyField(
        'User', 'tasks', verbose_name='任务执行者',
        db_table='team_task_executor')

    create_time = models.DateTimeField(
        '创建时间', default=datetime.now, db_index=True)

    enabled = TeamTaskManager()

    class Meta:
        db_table = 'team_task'
        ordering = ['-create_time']


class TeamTaskMarkerManager(models.Manager):
    def get_queryset(self):
        return super(TeamTaskMarkerManager, self).get_queryset().filter(
            user__is_enabled=True)


class TeamTaskMarker(models.Model):
    """
    任务完成标记信息

    """
    task = models.OneToOneField(
        'TeamTask', models.CASCADE, related_name='marker')
    user = models.ForeignKey(
        'User', models.CASCADE, '+', verbose_name='标记者')

    description = models.TextField(
        '备注', max_length=100, default='', db_index=True)
    create_time = models.DateTimeField(
        '标记时间', default=datetime.now, db_index=True)

    class Meta:
        db_table = 'team_task_marker'

    enabled = TeamTaskMarkerManager()

    @classmethod
    def exist(cls, user, task):
        """
        检查user是否标记任务为已完成

        """
        return cls.enabled.filter(task=task, user=user).exists()
