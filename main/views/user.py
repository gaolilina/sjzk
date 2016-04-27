from django import forms
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from main.decorators import require_token, validate_input, \
    require_token_and_validate_input, require_token_and_validate_json_input, \
    check_user_id
from main.models.location import get_location, set_location
from main.models.tag import get_tags, set_tags
from main.models.user import User, decrypt_phone_number, create_user
from main.models.visitor import update_visitor
from main.responses import *


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

    @method_decorator(require_token_and_validate_input(get_dict))
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

    @method_decorator(validate_input(post_dict))
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

    @method_decorator(validate_input(post_dict))
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


class Profile(View):
    @method_decorator(require_token)
    @method_decorator(check_user_id())
    def get(self, request, user):
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
    @method_decorator(check_user_id(True))
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


class EducationExperience(View):
    @method_decorator(require_token)
    @method_decorator(check_user_id())
    def get(self, request, user, sn=None):
        """
        获取用户的某个或所有教育经历

        :return:
            count: 经历总数
            list: 经历列表
                school: 学校
                degree: 学历
                    0: 其他 1: 初中 2: 高中 3: 大专
                    4: 本科 5: 硕士 6: 博士
                major: 专业
                begin_time: 入学时间
                end_time: 毕业时间
        """
        if not sn:
            exps = user.education_experiences.all()
        else:
            try:
                exps = [user.education_experiences.all()[int(sn)]]
            except IndexError:
                return Http404('experience not exists')

        c = user.education_experiences.count()
        l = [{
                 'school': e.school,
                 'degree': e.degree,
                 'major': e.major,
                 'begin_time': e.begin_time.strftime('%Y-%m-%d'),
                 'end_time': e.end_time.strftime('%Y-%m-%d'),
             } for e in exps]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'school': forms.CharField(max_length=20),
        'degree': forms.IntegerField(min_value=0, max_value=6),
        'major': forms.CharField(required=False, max_length=20),
        'begin_time': forms.DateField(),
        'end_time': forms.DateField(),
    }

    @method_decorator(require_token_and_validate_json_input(post_dict))
    @method_decorator(check_user_id(True))
    def post(self, request, data, sn=None):
        """
        增加或修改教育经历

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

        if not sn:
            e = exps.model(user=request.user)
        else:
            try:
                e = exps.all()[int(sn)]
            except IndexError:
                return Http404('experience not exists')

        if data['begin_time'] > data['end_time']:
            return Http400('invalid time data')

        for k in data:
            setattr(e, k, data[k])
        e.save()

        return Http200()

    @method_decorator(require_token)
    @method_decorator(check_user_id(True))
    def delete(self, request, sn=None):
        """
        删除用户的某个或所有教育经历

        """
        exps = request.user.education_experiences

        if not sn:
            exps.all().delete()
        else:
            try:
                e = exps.all()[int(sn)]
            except IndexError:
                return Http404('experience not exists')
            else:
                e.delete()

        return Http200()


class WorkExperience(View):
    @method_decorator(require_token)
    @method_decorator(check_user_id())
    def get(self, request, user, sn=None, is_fieldwork=False):
        """
        获取用户的某个或所有实习/工作经历

        :return:
            count: 经历总数
            list: 经历列表
                company: 公司
                position: 职位
                description: 工作内容描述
                begin_time: 入职时间
                end_time: 离职时间
        """
        if not sn:
            exps = user.fieldwork_experiences.all() \
                if is_fieldwork else user.work_experiences.all()
        else:
            try:
                exps = [user.fieldwork_experiences.all()[int(sn)]] \
                    if is_fieldwork \
                    else [user.work_experiences.all()[int(sn)]]
            except IndexError:
                return Http404('experience not exists')

        c = user.fieldwork_experiences.count() \
            if is_fieldwork else user.work_experiences.count()
        l = [{
                 'company': e.company,
                 'position': e.position,
                 'description': e.description,
                 'begin_time': e.begin_time.strftime('%Y-%m-%d'),
                 'end_time': e.end_time.strftime(
                     '%Y-%m-%d') if e.end_time else None,
             } for e in exps]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'company': forms.CharField(max_length=20),
        'position': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'begin_time': forms.DateField(),
        'end_time': forms.DateField(required=False),
    }

    @method_decorator(require_token_and_validate_json_input(post_dict))
    @method_decorator(check_user_id(True))
    def post(self, request, data, sn=None, is_fieldwork=False):
        """
        增加或修改实习/工作经历

        :param data:
            company: 公司（必填）
            position: 职位（必填）
            description: 工作内容描述
            begin_time: 入职时间（必填）
            end_time: 离职时间（用 None 表示在职）
        """
        exps = request.user.fieldwork_experiences \
            if is_fieldwork else request.user.work_experiences

        if not sn:
            e = exps.model(user=request.user)
        else:
            try:
                e = exps.all()[int(sn)]
            except IndexError:
                return Http404('experience not exists')

        if 'end_time' in data and data['end_time'] \
                and data['begin_time'] > data['end_time']:
            return Http400('invalid time data')

        for k in data:
            setattr(e, k, data[k])
        e.save()

        return Http200()

    @method_decorator(require_token)
    @method_decorator(check_user_id(True))
    def delete(self, request, sn=None, is_fieldwork=False):
        """
        删除用户的某个或所有工作/实习经历

        """
        exps = request.user.fieldwork_experiences \
            if is_fieldwork else request.user.work_experiences

        if not sn:
            exps.all().delete()
        else:
            try:
                e = exps.all()[int(sn)]
            except IndexError:
                return Http404('experience not exists')
            else:
                e.delete()

        return Http200()
