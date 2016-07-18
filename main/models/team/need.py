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

    type = None
    title = models.TextField(
            '需求标题', max_length=20, db_index=True)
    status = models.IntegerField(
            '状态', default=0, choices=(
            ('未满足', 0), ('已满足', 1), ('已删除', 2)))
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


class TeamMemberNeed(TeamNeed):
    """
    人员需求
    """
    type = models.IntegerField(
            '需求类型', default=1)
    age_min = models.IntegerField(
            '最小年龄', default='')
    age_max = models.IntegerField(
            '最大年龄', default='')
    gender = models.IntegerField(
            '性别要求', default=0, choices=(('不限', 0), ('男', 1), ('女', 2)))

    degree = models.IntegerField(
        '学历', default=0, choices=(
            ('其他', 0), ('初中', 1), ('高中', 2), ('大专', 3),
            ('本科', 4), ('硕士', 5), ('博士', 6)))
    major = models.CharField(
        '专业', max_length=20, default='', db_index=True)
    graduate_time = models.DateField(
        '毕业时间', default='', db_index=True)
    work_experience = models.CharField(
            '工作经历', max_length=100, default='', db_index=True)
    practice_experience = models.CharField(
            '实习经历', max_length=100, default='', db_index=True)
    project_experience = models.CharField(
            '项目经历', max_length=100, default='', db_index=True)

    class Meta:
        db_table = 'member_need'


class TeamOutsourceNeed(TeamNeed):
    """
    外包需求
    """
    type = models.IntegerField(
            '需求类型', default=2)
    age_min = models.IntegerField(
            '最小年龄', default='')
    age_max = models.IntegerField(
            '最大年龄', default='')
    gender = models.IntegerField(
            '性别要求', default=0, choices=(('不限', 0), ('男', 1), ('女', 2)))
    degree = models.IntegerField(
        '学历', default=0, choices=(
            ('其他', 0), ('初中', 1), ('高中', 2), ('大专', 3),
            ('本科', 4), ('硕士', 5), ('博士', 6)))
    major = models.CharField(
        '专业', max_length=20, default='', db_index=True)
    expend = models.IntegerField('费用', default=-1)
    expend_unit = models.IntegerField(
            '费用单位', default=0, choices=(('项', 0), ('天', 1), ('人', 2)))
    description = models.TextField(
            '需求描述', max_length=100, default='', db_index=True)
    start_time = models.DateTimeField(
            '开始时间', default=datetime.now, db_index=True)
    end_time = models.DateTimeField(
            '结束时间', default='', db_index=True)

    class Meta:
        db_table = 'outsource_need'


class TeamUndertakeNeed(TeamNeed):
    """
    承接需求
    """
    type = models.IntegerField(
            '需求类型', default=3)
    expend = models.IntegerField('费用')
    expend_unit = models.IntegerField(
            '费用单位', choices=(('项', 0), ('天', 1), ('人', 2)))
    description = models.TextField(
            '需求描述', max_length=100, db_index=True)
    start_time = models.DateTimeField(
            '开始时间', default=datetime.now, db_index=True)
    end_time = models.DateTimeField(
            '结束时间', default='', db_index=True)

    class Meta:
        db_table = 'undertake_need'
