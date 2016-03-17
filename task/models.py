from django.db import models
from django.utils import timezone

from project.models import Project
from user.models import User


class Task(models.Model):
    """
    任务信息

    """
    project = models.ForeignKey(Project, models.CASCADE, 'tasks', 'task')
    name = models.CharField('任务名称', max_length=20, db_index=True)
    description = models.TextField('任务描述', max_length=100, db_index=True)
    status = models.IntegerField(
        '任务状态', default=0, db_index=True,
        choices=(('未完成', 0), ('已完成', 1), ('已取消', 2)))
    create_time = models.DateTimeField(
        '创建时间', default=timezone.now, db_index=True)
    expected_finish_time = models.DateTimeField(
        '预期完成时间', default=None, blank=True, null=True, db_index=True)
    actual_finish_time = models.DateTimeField(
        '实际完成时间', default=None, blank=True, null=True, db_index=True)
    executors = models.ManyToManyField(
        User, 'tasks', 'task',
        verbose_name='任务执行者', db_table='task_executors')

    class Meta:
        db_table = 'project_task'
        ordering = ['-create_time']

    def __repr__(self):
        return "<Task - %s (%s)>" % (self.name, self.project.name)


class TaskFinishMarker(models.Model):
    """
    任务完成标记信息

    """
    task = models.OneToOneField(
        Task, models.CASCADE, related_name='finish_marker')
    user = models.ForeignKey(
        User, models.CASCADE, '+', verbose_name='标记者')
    description = models.TextField(
        '备注', max_length=100, default='', db_index=True)
    time = models.DateTimeField('标记时间', default=timezone.now, db_index=True)

    class Meta:
        db_table = 'project_task_finish_marker'

    def __repr__(self):
        return '<Task Finish Marker - %s (%s)>' % (
            self.task.name, self.user.name)
