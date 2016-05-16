from django import forms
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input, process_uploaded_image
from main.models import User
from main.models.location import Location
from main.models.tag import Tag
from main.models.visitor import Visitor
from main.responses import *


class Users(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'name', '-name',
    ]

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取用户列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = User.enabled.count()
        users = User.enabled.order_by(k)[i:j]
        l = [{'id': u.id,
              'username': u.username,
              'name': u.name,
              'icon_url': u.icon_url,
              'create_time': u.create_time} for u in users]
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
            phone_number = User.decrypt_phone_number(phone_number)
            user = User.create(phone_number, password)
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


class Username(View):
    @require_token
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

    @require_token
    @validate_input(post_dict)
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

    @require_token
    @validate_input(post_dict)
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


class Icon(View):
    @check_object_id(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        """
        获取用户头像URL

        :return:
            icon_url: url | null
        """
        user = user or request.user

        url = user.icon_url
        return JsonResponse({'icon_url': url})


class IconSelf(Icon):
    @require_token
    @process_uploaded_image('icon')
    def post(self, request, icon):
        """
        设置当前用户的头像

        """
        if request.user.icon:
            request.user.icon.delete()
        request.user.icon = icon
        request.user.save()
        return Http200()


class Profile(View):
    @check_object_id(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        """
        获取用户的基本资料

        :return:
            username: 用户名
            name: 昵称
            icon_url: 用户头像URL
            create_time: 注册时间
            description: 个人简介
            email: 电子邮箱
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日
            location: 所在地区，格式：[province_id, city_id]
            tags: 标签，格式：['tag1', 'tag2', ...]
        """
        user = user or request.user

        # 更新访客记录
        if user != request.user:
            Visitor.update(user, request.user)

        r = dict()
        r['username'] = user.username
        r['name'] = user.name
        r['icon'] = user.icon_url
        r['create_time'] = user.create_time
        r['description'] = user.profile.description
        r['email'] = user.profile.email
        r['gender'] = user.profile.gender
        r['birthday'] = user.profile.birthday if user.profile.birthday else None
        r['location'] = Location.get(user)
        r['tags'] = Tag.get(user)

        return JsonResponse(r)


class ProfileSelf(Profile):
    post_dict = {
        'name': forms.CharField(required=False, min_length=1, max_length=15),
        'description': forms.CharField(required=False, max_length=100),
        'email': forms.EmailField(required=False),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'birthday': forms.DateField(required=False),
    }

    @require_token
    @validate_json_input(post_dict)
    def post(self, request, data):
        """
        修改用户资料

        :param data:
            name: 昵称
            description: 个人简介
            email: 电子邮箱
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日
            location: 所在地区，格式：[province_id, city_id]
            tags: 标签，格式：['tag1', 'tag2', ...]

        """
        name = data.pop('name') if 'name' in data else None
        location = data.pop('location') if 'location' in data else None
        tags = data.pop('tags') if 'tags' in data else None

        profile = request.user.profile
        for k, v in data.items():
            setattr(profile, k, v)

        error = ''
        try:
            with transaction.atomic():
                if location:
                    try:
                        Location.set(request.user, location)
                    except TypeError:
                        error = 'invalid location'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                    else:
                        request.user.location.save()
                if tags:
                    try:
                        Tag.set(request.user, tags)
                    except TypeError:
                        error = 'invalid tag list'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                if name:
                    request.user.name = name
                    request.user.save()
                profile.save()
        except IntegrityError:
            return Http400(error)
        else:
            return Http200()


class Identification(View):
    @check_object_id(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        """
        获取用户的身份信息，身份证号仅对本人可见

        :return:
            is_verified: 是否通过实名认证
            name: 真实姓名
            id_number: 身份证号
            school: 所在学校
            student_number: 学生证号
        """
        user = user or request.user

        i = user.identification
        l = {'is_verified': i.is_verified,
             'name': i.name,
             'school': i.school,
             'student_number': i.student_number}
        if user == request.user:
            l['id_number'] = i.id_number
        return JsonResponse(l)


class IdentificationSelf(Identification):
    post_dict = {
        'name': forms.CharField(required=False, min_length=1, max_length=15),
        'id_number': forms.RegexField(
            r'^[0-9xX]{18}$', required=False, strip=True),
        'school': forms.CharField(required=False, max_length=20),
        'student_number': forms.RegexField(
            r'^[0-9]{,15}$', required=False, strip=True),
    }

    @require_token
    @validate_json_input(post_dict)
    def post(self, request, data):
        """
        修改用户身份信息，已通过实名认证后禁止修改身份证号与姓名

        :param data:
            name: 真实姓名
            id_number: 身份证号
            school: 所在学校
            student_number: 学生证号
        """
        identification = request.user.identification
        if identification.is_verified and (
                        'name' in data or 'id_number' in data):
            return Http403('user has been verified')

        for k, v in data.items():
            setattr(identification, k, v)
        identification.save()
        return Http200()


# todo: test id card
class IDCard(View):
    @require_token
    def get(self, request):
        """
        判断是否已上传身份证照片

        """
        return Http200() if request.user.identification.id_card \
            else Http404()

    @require_token
    @process_uploaded_image('id_card')
    def post(self, request, id_card):
        """
        设置当前用户的身份证照片

        """
        if request.user.identification.is_verified:
            return Http403('user has been verified')
        else:
            if request.user.identification.id_card:
                request.user.identification.id_card.delete()
            request.user.identification.id_card = id_card
            request.user.identification.save()
            return Http200()


# todo: test student card
class StudentCard(View):
    @require_token
    def get(self, request):
        """
        判断是否已上传身份证照片

        """
        return Http200() if request.user.identification.student_card \
            else Http404()

    @require_token
    @process_uploaded_image('student_card')
    def post(self, request, student_card):
        """
        设置当前用户的学生证照片

        """
        if request.user.identification.is_verified:
            return Http403('user has been verified')
        else:
            if request.user.identification.student_card:
                request.user.identification.student_card.delete()
            request.user.identification.student_card = student_card
            request.user.identification.save()
            return Http200()
