from django.db import models

from user.models import User


class UserProfile(models.Model):
    """
    APP用户基本资料

    """
    user = models.OneToOneField(User, models.CASCADE, related_name='profile')

    description = models.TextField(
        '个人简介', max_length=100, default='', db_index=True)
    gender = models.IntegerField(
        '性别', default=0, choices=(('保密', 0), ('男', 1), ('女', 1)))
    birthday = models.DateField(
        '出生日期', default=None, blank=True, null=True)
    icon = models.ImageField('用户头像')

    class Meta:
        db_table = 'user_profile'

    def __repr__(self):
        return '<User Profile - %s>' % self.user.name


class UserIdentification(models.Model):
    """
    APP用户身份信息

    """
    user = models.OneToOneField(
        User, models.CASCADE, related_name='identification')

    is_verified = models.BooleanField(
        '是否已通过实名认证', default=False, db_index=True)
    name = models.CharField(
        '真实姓名', max_length=10, default='', db_index=True)
    number = models.CharField('身份证号', max_length=18, default='')
    photo = models.ImageField('身份证照片')

    class Meta:
        db_table = 'user_identification'

    def __repr__(self):
        return '<User Identification - %s>' % self.user.name


class UserStudentIdentification(models.Model):
    """
    APP用户学生信息

    """
    user = models.OneToOneField(
        User, models.CASCADE, related_name='student_identification')

    school = models.CharField('学校名称', max_length=20, default='')
    number = models.CharField('学生证号', max_length=20, default='')
    photo = models.ImageField('学生证照片')

    class Meta:
        db_table = 'user_student_identification'

    def __repr__(self):
        return '<User Student Identification - %s>' % self.user.name


class UserEducationExperience(models.Model):
    """
    APP用户教育经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'education_experiences', 'education_experience')

    school = models.CharField('学校', max_length=20, default='')
    degree = models.CharField('学历', max_length=2, default='')
    major = models.CharField('专业', max_length=20, default='')
    begin_time = models.DateField(
        '入学时间', default=None, blank=True, null=True)
    end_time = models.DateField(
        '毕业时间', default=None, blank=True, null=True)

    order = models.IntegerField('序号')

    class Meta:
        db_table = 'user_education_experience'
        ordering = ['order']

    def __repr__(self):
        return '<User Education Experience %s - %s>' % (
            self.order, self.user.name)


class UserFieldworkExperience(models.Model):
    """
    APP用户实习经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'fieldwork_experiences', 'fieldwork_experience')

    company = models.CharField('公司', max_length=20, default='')
    position = models.CharField('职位', max_length=20, default='')
    begin_time = models.DateField(
        '入职时间', default=None, blank=True, null=True)
    end_time = models.DateField(
        '离职时间', default=None, blank=True, null=True)

    order = models.IntegerField('序号')

    class Meta:
        db_table = 'user_fieldwork_experience'
        ordering = ['order']

    def __repr__(self):
        return '<User Fieldwork Experience %s - %s>' % (
            self.order, self.user.name)


class UserWorkExperience(models.Model):
    """
    APP用户工作经历

    """
    user = models.ForeignKey(
        User, models.CASCADE, 'work_experiences', 'work_experience')

    company = models.CharField('公司', max_length=20, default='')
    position = models.CharField('职位', max_length=20, default='')
    begin_time = models.DateField(
        '入职时间', default=None, blank=True, null=True)
    end_time = models.DateField(
        '离职时间', default=None, blank=True, null=True)

    order = models.IntegerField('序号')

    class Meta:
        db_table = 'user_work_experience'
        ordering = ['order']

    def __repr__(self):
        return '<User Work Experience %s - %s>' % (
            self.order, self.user.name)
