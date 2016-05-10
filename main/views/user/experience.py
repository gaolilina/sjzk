from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import check_object_id, require_token, validate_json_input
from main.models import User, UserEducationExperience, UserWorkExperience, \
    UserFieldworkExperience
from main.responses import *


class EditableEEMixin(object):
    # 可编辑的教育经历Mixin
    post_dict = {
        'school': forms.CharField(max_length=20),
        'degree': forms.IntegerField(min_value=0, max_value=6),
        'major': forms.CharField(required=False, max_length=20),
        'begin_time': forms.DateField(),
        'end_time': forms.DateField(),
    }

    @validate_json_input(post_dict)
    def update(self, request, exp, data):
        """
        增加或修改当前用户的教育经历

        :param data:
            school: 学校（必填）
            degree: 学位（必填）
                0: 其他 1: 初中 2: 高中 3: 大专
                4: 本科 5: 硕士 6: 博士
            major: 专业
            begin_time: 入学时间（必填）
            end_time: 毕业时间（必填）
        """
        if data['begin_time'] > data['end_time']:
            return Http400('invalid data "time"')

        for k in data:
            setattr(exp, k, data[k])
        exp.save()
        return Http200()


class EditableWEMixin(object):
    # 可编辑的工作经历Mixin
    post_dict = {
        'company': forms.CharField(max_length=20),
        'position': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'begin_time': forms.DateField(),
        'end_time': forms.DateField(required=False),
    }

    @validate_json_input(post_dict)
    def update(self, request, exp, data):
        """
        增加或修改实习/工作经历

        :param data:
            company: 公司（必填）
            position: 职位（必填）
            description: 工作内容描述
            begin_time: 入职时间（必填）
            end_time: 离职时间（用 None 表示在职）
        """
        if 'end_time' in data and data['end_time'] \
                and data['begin_time'] > data['end_time']:
            return Http400('invalid data "time"')

        for k in data:
            setattr(exp, k, data[k])
        exp.save()
        return Http200()


# 用于所有用户
class EducationExperiences(View):
    @check_object_id(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        """
        获取用户的教育经历

        :return:
            count: 经历总数
            list: 经历列表
                id: 该记录的ID
                school: 学校
                degree: 学历
                    0: 其他 1: 初中 2: 高中 3: 大专
                    4: 本科 5: 硕士 6: 博士
                major: 专业
                begin_time: 入学时间
                end_time: 毕业时间
        """
        if not user:
            user = request.user
        exps = user.education_experiences.all()

        c = user.education_experiences.count()
        l = [{
                 'id': e.id,
                 'school': e.school,
                 'degree': e.degree,
                 'major': e.major,
                 'begin_time': e.begin_time,
                 'end_time': e.end_time,
             } for e in exps]
        return JsonResponse({'count': c, 'list': l})


class WorkExperiences(View):
    attr = 'work_experiences'

    @check_object_id(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        """
        获取用户的工作经历

        :return:
            count: 经历总数
            list: 经历列表
                id: 该记录的ID
                company: 公司
                position: 职位
                description: 工作内容描述
                begin_time: 入职时间
                end_time: 离职时间
        """
        if not user:
            user = request.user

        exps = getattr(user, self.attr).all()

        c = getattr(user, self.attr).count()
        l = [{
                 'company': e.company,
                 'position': e.position,
                 'description': e.description,
                 'begin_time': e.begin_time,
                 'end_time': e.end_time if e.end_time else None,
             } for e in exps]
        return JsonResponse({'count': c, 'list': l})


class FieldworkExperiences(WorkExperiences):
    attr = 'fieldwork_experiences'


# 用于当前用户多个资源
class EducationExperiencesSelf(EducationExperiences, EditableEEMixin):
    @require_token
    def post(self, request):
        """
        增加一条教育经历

        """
        exp = request.user.education_experiences.model(user=request.user)
        return self.update(request, exp)

    @require_token
    def delete(self, request):
        """
        删除当前用户的某个或所有教育经历

        """
        request.user.education_experiences.all().delete()
        return Http200()


class WorkExperiencesSelf(WorkExperiences, EditableWEMixin):
    attr = 'work_experiences'

    @require_token
    def post(self, request):
        """
        增加一条实习/工作经历

        """
        exp = getattr(request.user, self.attr).model(user=request.user)
        return self.update(request, exp)

    @require_token
    def delete(self, request):
        """
        删除用户的所有工作/实习经历

        """
        getattr(request.user, self.attr).all().delete()
        return Http200()


class FieldworkExperiencesSelf(WorkExperiencesSelf):
    attr = 'fieldwork_experiences'


# 用于当前用户单个资源
class EducationExperience(View, EditableEEMixin):
    @require_token
    @check_object_id(UserEducationExperience.objects, 'exp')
    def post(self, request, exp):
        if exp.user != request.user:
            return Http403('not current user\'s object')
        return self.update(request, exp)

    @require_token
    @check_object_id(UserEducationExperience.objects, 'exp')
    def delete(self, request, exp):
        if exp.user != request.user:
            return Http403('not current user\'s object')
        exp.delete()
        return Http200()


class WorkExperience(View, EditableWEMixin):
    @require_token
    @check_object_id(UserWorkExperience.objects, 'exp')
    def post(self, request, exp):
        if exp.user != request.user:
            return Http403('not current user\'s object')
        return self.update(request, exp)

    @require_token
    @check_object_id(UserWorkExperience.objects, 'exp')
    def delete(self, request, exp):
        if exp.user != request.user:
            return Http403('not current user\'s object')
        exp.delete()
        return Http200()


class FieldworkExperience(View, EditableWEMixin):
    @require_token
    @check_object_id(UserFieldworkExperience.objects, 'exp')
    def post(self, request, exp):
        if exp.user != request.user:
            return Http403('not current user\'s object')
        return self.update(request, exp)

    @require_token
    @check_object_id(UserFieldworkExperience.objects, 'exp')
    def delete(self, request, exp):
        if exp.user != request.user:
            return Http403('not current user\'s object')
        exp.delete()
        return Http200()

