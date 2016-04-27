from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from main.decorators import require_token, check_object_id, \
    require_token_and_validate_json_input
from main.models import User
from main.responses import *


# 用于其他用户
class EducationExperiencesReadOnly(View):
    @method_decorator(require_token)
    @method_decorator(check_object_id(User.enabled, 'user_id', 'user'))
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
                 'begin_time': e.begin_time.strftime('%Y-%m-%d'),
                 'end_time': e.end_time.strftime('%Y-%m-%d'),
             } for e in exps]
        return JsonResponse({'count': c, 'list': l})


# 用于当前用户单条数据
class EducationExperiencesWriteOnly(View):
    post_dict = {
        'school': forms.CharField(max_length=20),
        'degree': forms.IntegerField(min_value=0, max_value=6),
        'major': forms.CharField(required=False, max_length=20),
        'begin_time': forms.DateField(),
        'end_time': forms.DateField(),
    }

    @method_decorator(require_token_and_validate_json_input(post_dict))
    def post(self, request, data, exp_id=None):
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
        exps = request.user.education_experiences

        if not exp_id:
            e = exps.model(user=request.user)
        else:
            try:
                e = exps.get(id=int(exp_id))
            except ObjectDoesNotExist:
                return Http404('object not exists')

        if data['begin_time'] > data['end_time']:
            return Http400('invalid data "time"')

        for k in data:
            setattr(e, k, data[k])
        e.save()
        return Http200()

    @method_decorator(require_token)
    def delete(self, request, exp_id=None):
        """
        删除当前用户的某个或所有教育经历

        """
        exps = request.user.education_experiences

        if not exp_id:
            exps.all().delete()
        else:
            try:
                e = exps.get(id=int(exp_id))
            except ObjectDoesNotExist:
                return Http404('object not exists')
            else:
                e.delete()

        return Http200()


# 用于当前用户
class EducationExperiences(EducationExperiencesReadOnly,
                           EducationExperiencesWriteOnly):
    pass


# 用于其他用户
class WorkExperiencesReadOnly(View):
    attr = 'work_experiences'

    @method_decorator(require_token)
    @method_decorator(check_object_id(User.enabled, 'user_id', 'user'))
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
                 'begin_time': e.begin_time.strftime('%Y-%m-%d'),
                 'end_time': e.end_time.strftime(
                     '%Y-%m-%d') if e.end_time else None,
             } for e in exps]
        return JsonResponse({'count': c, 'list': l})


# 用于当前用户单条数据
class WorkExperiencesWriteOnly(View):
    attr = 'work_experiences'
    post_dict = {
        'company': forms.CharField(max_length=20),
        'position': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'begin_time': forms.DateField(),
        'end_time': forms.DateField(required=False),
    }

    @method_decorator(require_token_and_validate_json_input(post_dict))
    def post(self, request, data, exp_id=None):
        """
        增加或修改实习/工作经历

        :param data:
            company: 公司（必填）
            position: 职位（必填）
            description: 工作内容描述
            begin_time: 入职时间（必填）
            end_time: 离职时间（用 None 表示在职）
        """
        exps = getattr(request.user, self.attr)

        if not exp_id:
            e = exps.model(user=request.user)
        else:
            try:
                e = exps.get(id=int(exp_id))
            except ObjectDoesNotExist:
                return Http404('object not exists')

        if 'end_time' in data and data['end_time'] \
                and data['begin_time'] > data['end_time']:
            return Http400('invalid data "time"')

        for k in data:
            setattr(e, k, data[k])
        e.save()
        return Http200()

    @method_decorator(require_token)
    def delete(self, request, exp_id=None):
        """
        删除用户的某个或所有工作/实习经历

        """
        exps = getattr(request.user, self.attr)

        if not exp_id:
            exps.all().delete()
        else:
            try:
                e = exps.get(id=int(exp_id))
            except ObjectDoesNotExist:
                return Http404('experience not exists')
            else:
                e.delete()

        return Http200()


# 用于当前用户
class WorkExperiences(WorkExperiencesReadOnly, WorkExperiencesWriteOnly):
    pass


# 用于其他用户
class FieldworkExperiencesReadOnly(WorkExperiencesReadOnly):
    attr = 'fieldwork_experiences'


# 用于当前用户单条数据
class FieldworkExperiencesWriteOnly(WorkExperiencesWriteOnly):
    attr = 'fieldwork_experiences'


# 用于当前用户
class FieldworkExperiences(FieldworkExperiencesReadOnly,
                           FieldworkExperiencesWriteOnly):
    pass
