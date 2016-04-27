from django import forms
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from main.decorators import require_token, validate_input, \
    require_token_and_validate_input, require_token_and_validate_json_input, \
    check_object_id
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


class ProfileReadOnly(View):
    @method_decorator(check_object_id(User.enabled, 'user_id', 'user'))
    @method_decorator(require_token)
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


class Profile(ProfileReadOnly):
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
