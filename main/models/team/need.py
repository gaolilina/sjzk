from datetime import datetime

from django.db import models
from main.models.user.experience import WorkExperience


class NeedEducationExperience(WorkExperience):
    """
    教育经历需求
    """
    need = models.ForeignKey('TeemNeed', models.CASCADE, 'education_experience')

    class Meta:
        db_table = 'need_education_experience'


class NeedWorkExperience(WorkExperience):
    """
    工作经历需求
    """
    need = models.ForeignKey('TeemNeed', models.CASCADE, 'work_experience')

    class Meta:
        db_table = 'need_work_experience'


class NeedFieldworkExperience(WorkExperience):
    """
    实习经历需求

    """
    need = models.ForeignKey('TeemNeed', models.CASCADE,
                             'fieldwork_experiences')

    class Meta:
        db_table = 'need_fieldwork_experience'


class NeedProjectExperience(WorkExperience):
    """
    需求项目经历
    """
    need = models.ForeignKey('TeemNeed', models.CASCADE, 'project_experience')

    class Meta:
        db_table = 'need_project_experience'


class TeamNeedManager(models.Manager):
    def get_queryset(self):
        return super(TeamNeedManager, self).get_queryset().filter(
            team__is_enabled=True)


class TeamNeed(models.Model):
    """
    团队需求信息

    """
    team = models.ForeignKey('Team', models.CASCADE, 'needs')

    title = models.TextField(
            '需求标题', max_length=20, db_index=True)
    status = models.IntegerField(
            '状态', default=0, choices=(('未满足', 0), ('已满足', 1)))
    number = models.IntegerField(
            '需求人数', default=-1, db_index=True)
    field = models.CharField(
            '领域', max_length=10, db_index=True)
    skills = models.CharField(
            '技能', max_length=10, db_index=True)

    create_time = models.DateTimeField(
            '创建时间', default=datetime.now, db_index=True)
    deadline = models.DateTimeField(
        '截止时间', default=None, blank=True, null=True, db_index=True)
    update_time = models.DateTimeField(
            '更新时间', auto_now=True, db_index=True)

    enabled = TeamNeedManager()

    class Meta:
        ordering = ['-create_time']


class MemberNeed(TeamNeed):
    """
    人员需求
    """
    age = models.CharField(
            '年龄区间', default='不限')
    gender = models.IntegerField(
            '性别要求', default=0, choices=(('不限', 0), ('男', 1), ('女', 2)))
    qualification = models.CharField()
    graduate_time = models.TimeField()
    profession = models.CharField()
    work_experience = models.CharField()
    practice_experience = models.CharField()
    project_experience = models.CharField()

    class Meta:
        db_table = 'member_need'


class OutsourceNeed(TeamNeed):
    """
    外包需求
    """
    age = models.CharField(
            '年龄区间', default='不限')
    gender = models.IntegerField(
            '性别要求', default=0, choices=(('不限', 0), ('男', 1), ('女', 2)))
    qualification = models.CharField()
    profession = models.CharField()
    expend = models.IntegerField('费用')
    expend_unit = models.IntegerField(
            '费用单位', choices=(('项', 0), ('天', 1), ('人', 2)))
    description = models.TextField(
            '需求描述', max_length=100, db_index=True)
    task_time = models.TimeField('任务时间区间')

    class Meta:
        db_table = 'outsource_need'


class UndertakeNeed(TeamNeed):
    """
    承接需求
    """
    expend = models.IntegerField('费用')
    expend_unit = models.IntegerField(
            '费用单位', choices=(('项', 0), ('天', 1), ('人', 2)))
    description = models.TextField(
            '需求描述', max_length=100, db_index=True)
    undertake_time = models.TimeField('承接时间区间')

    class Meta:
        db_table = 'undertake_need'
