from django.db import models

from main.models.user import User


class WorkExperience(models.Model):
    """
    用户工作/实习经历基类

    """
    company = models.CharField(
        '公司', max_length=20, default='', db_index=True)
    position = models.CharField(
        '职位', max_length=20, default='', db_index=True)
    description = models.TextField(
        '工作内容描述', max_length=100, default='', db_index=True)
    begin_time = models.DateField(
        '入职时间', db_index=True)
    end_time = models.DateField(
        '离职时间', default=None, null=True, db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    class Meta:
        abstract = True


class UserWorkExperience(WorkExperience):
    """
    用户工作经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'work_experiences', 'work_experience')

    class Meta:
        db_table = 'user_work_experience'
        ordering = ['id']

    def __repr__(self):
        return '<User Work Experience - %s>' % self.user.name


class UserFieldworkExperience(WorkExperience):
    """
    用户实习经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'fieldwork_experiences', 'fieldwork_experience')

    class Meta:
        db_table = 'user_fieldwork_experience'
        ordering = ['id']

    def __repr__(self):
        return '<User Fieldwork Experience - %s>' % self.user.name


class UserEducationExperience(models.Model):
    """
    用户教育经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'education_experiences', 'education_experience')

    school = models.CharField(
        '学校', max_length=20, default='', db_index=True)
    degree = models.IntegerField(
        '学历', default=0, choices=(
            ('其他', 0), ('初中', 1), ('高中', 2), ('大专', 3),
            ('本科', 4), ('硕士', 5), ('博士', 6)))
    major = models.CharField(
        '专业', max_length=20, default='', db_index=True)
    begin_time = models.DateField(
        '入学时间', db_index=True)
    end_time = models.DateField(
        '毕业时间', db_index=True)
    update_time = models.DateTimeField(
        '更新时间', auto_now=True, db_index=True)

    class Meta:
        db_table = 'user_education_experience'
        ordering = ['id']

    def __repr__(self):
        return '<User Education Experience - %s>' % self.user.name
