from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from main.decorators import require_token, require_token_and_validate_input, \
    require_token_and_validate_json_input
from main.models.location import set_location
from main.models.tag import set_tags
from main.responses import *
from . import user


class Username(View):
    @method_decorator(require_token)
    def get(self, request):
        """
        获取当前用户的用户名（检查用户是否已设置用户名）

        :return:
            username: 用户名 | null
        """
        username = request.user.username
        return JsonResponse({'username': username})

    post_dict = {
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True),
    }

    @method_decorator(require_token_and_validate_input(post_dict))
    def post(self, request, username):
        """
        设置当前用户的用户名，存储时字母转换成小写
        用户名只能设置一次

        :param username: 匹配 ^[a-zA-Z0-9_]{4,15}$ 的字符串，且非纯数字

        """
        if request.user.username:
            return Http403('username already set')

        if username.isdigit():
            return Http400('invalid username')

        try:
            request.user.username = username.lower()
            request.user.save(update_fields=['username', 'update_time'])
            return Http200()
        except IntegrityError:
            return Http403('username is already used by others')


class Password(View):
    post_dict = {
        'new_password': forms.CharField(
            min_length=6, max_length=20, strip=False),
        'old_password': forms.CharField(
            min_length=6, max_length=20, strip=False),
    }

    @method_decorator(require_token_and_validate_input(post_dict))
    def post(self, request, old_password, new_password):
        """
        修改密码

        :param old_password: 旧密码
        :param new_password: 新密码（6-20位）

        """
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save(update_fields=['password'])
            return Http200()
        else:
            return Http403('failed when validating old password')


class Profile(user.Profile):
    post_dict = {
        'name': forms.CharField(required=False, min_length=1, max_length=15),
        'description': forms.CharField(required=False, max_length=100),
        'email': forms.EmailField(required=False),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'birthday': forms.DateField(required=False),
        'real_name': forms.CharField(required=False, max_length=15),
        'id_number': forms.RegexField(r'^\d{18}$', required=False, strip=True),
    }

    @method_decorator(require_token_and_validate_json_input(post_dict))
    def post(self, request, data):
        """
        修改用户资料

        :param data:
            name: 昵称
            description: 个人简介
            email: 电子邮箱
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日
            real_name: 真实姓名
            id_number: 身份证号
            location: 所在地区，格式：[province_id, city_id]
            tags: 标签，格式：['tag1', 'tag2', ...]

        """
        profile = request.user.profile

        normal_keys = ['name', 'description', 'email', 'gender', 'birthday']
        for k in normal_keys:
            if k in data:
                setattr(profile, k, data[k])

        identification_keys = ['real_name', 'id_number']
        for k in identification_keys:
            if k in data:
                if request.user.is_verified:
                    return Http403('user has been verified')
                else:
                    setattr(profile, k, data[k])

        error = ''
        try:
            with transaction.atomic():
                if 'location' in data:
                    try:
                        set_location(request.user, data['location'])
                    except TypeError:
                        error = 'invalid location'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                if 'tags' in data:
                    try:
                        set_tags(request.user, data['tags'])
                    except TypeError:
                        error = 'invalid tag list'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                profile.save()
        except IntegrityError:
            return Http400(error)
        else:
            return Http200()


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


class EducationExperiences(user.EducationExperiences,
                           EducationExperiencesWriteOnly):
    pass


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


class WorkExperiences(user.WorkExperiences, WorkExperiencesWriteOnly):
    pass


class FieldworkExperiencesWriteOnly(WorkExperiencesWriteOnly):
    attr = 'fieldwork_experiences'


class FieldworkExperiences(user.FieldworkExperiences,
                           FieldworkExperiencesWriteOnly):
    pass
