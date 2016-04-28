from django import forms
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, validate_input, check_object_id
from main.models.location import get_location
from main.models.tag import get_tags
from main.models.user import User, decrypt_phone_number, create_user
from main.models.visitor import update_visitor
from main.responses import *
from main.views import TokenRequiredView


class Users(View):
    get_dict = {
        'page': forms.IntegerField(required=False, min_value=0),
        'size': forms.IntegerField(required=False, min_value=10),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_order = [
        'create_time', '-create_time',
        'profile__name', '-profile__name',
    ]

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取用户列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间降序（默认值）
            1: 注册时间升序
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_order[order]
        c = User.enabled.count()
        users = User.enabled.order_by(k)[i:j]
        l = [{
                 'id': u.id,
                 'username': u.username,
                 'name': u.profile.name,
                 'create_time': u.create_time,
             } for u in users]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'phone_number': forms.CharField(),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
    }

    @validate_input(post_dict)
    def post(self, request, phone_number, password):
        """
        注册新用户

        :param phone_number: 加密后的手机号
        :param password: 密码，长度6-20位
        :return: 200 | 400 | 403
            token: 用户令牌
        """
        try:
            phone_number = decrypt_phone_number(phone_number)
            user = create_user(phone_number, password)
            return JsonResponse({'token': user.token.value})
        except ValueError as e:
            return Http400(e)
        except IntegrityError:
            return Http403('user already exists')


class Token(View):
    post_dict = {
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
    }

    @validate_input(post_dict)
    def post(self, request, username, password):
        """
        更新并获取用户令牌，纯数字“用户名”视为手机号

        :param username: 用户名或手机号
        :param password: 密码
        :return:
            token: 用户令牌
        """
        if username.isdigit():
            try:
                user = User.objects.get(phone_number=username)
            except User.DoesNotExist:
                return Http401('invalid credential')
        else:
            try:
                user = User.objects.get(username=username.lower())
            except User.DoesNotExist:
                return Http401('invalid credential')

        if not user.is_enabled:
            return Http403('user is blocked')

        if not user.check_password(password):
            return Http401('invalid credential')

        user.token.update()
        return JsonResponse({'token': user.token.value})


class Profile(TokenRequiredView):
    @check_object_id(User.enabled, 'user')
    def get(self, request, user=None):
        """
        获取用户资料，标注 * 的键值仅在获取自己的资料时返回

        :return:
            phone_number: 手机号*
            username: 用户名
            create_time: 注册时间
            name: 昵称
            description: 个人简介
            email: 电子邮箱
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日
            real_name: 真实姓名
            id_number: 身份证号*
            location: 所在地区，格式：[province_id, city_id]
            tags: 标签，格式：['tag1', 'tag2', ...]
        """
        if not user:
            user = request.user

        # 更新访客记录
        if user != request.user:
            update_visitor(request.user, user)

        r = dict()
        if user == request.user:
            r['phone_number'] = user.phone_number
            r['id_number'] = user.profile.id_number
        r['username'] = user.username
        r['create_time'] = user.create_time.strftime('%Y-%m-%d')
        r['name'] = user.profile.name
        r['description'] = user.profile.description
        r['email'] = user.profile.email
        r['gender'] = user.profile.gender
        r['birthday'] = user.profile.birthday.strftime('%Y-%m-%d') \
            if user.profile.birthday else None
        r['real_name'] = user.profile.real_name
        r['location'] = get_location(user)
        r['tags'] = get_tags(user)

        return JsonResponse(r)


class EducationExperiences(TokenRequiredView):
    @check_object_id(User.enabled, 'user')
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


class WorkExperiences(TokenRequiredView):
    attr = 'work_experiences'

    @check_object_id(User.enabled, 'user')
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


class FieldworkExperiences(WorkExperiences):
    attr = 'fieldwork_experiences'
