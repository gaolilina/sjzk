import re
from datetime import datetime

from django.db import IntegrityError, transaction
from django.http import \
    JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from location.tools import get_location, set_location
from tag.tools import get_tags, set_tags
from user.models import User, UserToken, UserProfile, UserIdentification, \
    UserStudentIdentification
from user.tools import decrypt_phone_info
from visit.tools import update_visitor
from web_service.decorators import web_service


def user(request):
    @web_service(method='GET')
    def get(request, data):
        """
        获取用户列表

        :param data:
            offset: 偏移量（默认值：0）
            limit: 数量上限（默认值：10）
            order: 排序方式
                0: 注册时间降序（默认值）
                1: 注册时间升序
                2: 昵称升序
                3: 昵称降序
        :return: JSON Array
            id: 用户ID
            name: 用户昵称
            create_time: 注册时间
        """
        i = 0 if 'offset' not in data else data['offset']
        j = (i + 10) if 'limit' not in data else (i + data['limit'])

        available_orders = [
            '-create_time',
            'create_time',
            'name',
            '-name',
        ]
        try:
            order = available_orders[data['order']]
        except (KeyError, IndexError):
            order = '-create_time'

        result = []
        users = User.enabled.order_by(order)[i:j]
        for user in users:
            result.append({
                'id': user.id,
                'name': user.name,
                'create_time': user.create_time.timestamp(),
            })

        return JsonResponse(result, safe=False)

    @web_service(require_token=False)
    def post(request, data):
        """
        注册新用户

        :param data:
            phone_info: 手机号信息
            password: 密码
        :return: 200 | 400
            token: 用户token
        """
        if len(data['password']) < 6:
            return HttpResponseBadRequest()

        try:
            phone_number = decrypt_phone_info(data['phone_info'])
            with transaction.atomic():
                user = User(phone_number=phone_number)
                user.set_password(data['password'])
                user.save()
                user.name = '创易用户 %s' % user.id
                user.save()
                token_info = UserToken(user=user)
                token_info.update()
            return JsonResponse({'token': token_info.token})
        except (ValueError, IntegrityError):
            return HttpResponseBadRequest()

    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return HttpResponseForbidden()


@web_service(method='GET')
def user_total(request):
    """
    获取用户总数

    :return:
        total: 用户总数
    """
    total = User.enabled.count()
    return JsonResponse({'total': total})


@web_service(require_token=False)
def user_token(request, data):
    """
    获取用户token

    :param data:
        username: 用户名或手机号
        password: 密码
    :return: 200 | 400 | 403
        token: 用户token
    """
    try:
        user = User.objects.get(phone_number=data['username'])
    except User.DoesNotExist:
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return HttpResponseBadRequest()

    if user.is_enabled and user.check_password(data['password']):
        user.token_info.update()
        return JsonResponse({'token': user.token_info.token})
    else:
        return HttpResponseForbidden()


def user_username(request):
    @web_service(method='GET')
    def get(request):
        """
        获取当前用户的用户名（检查用户是否已设置用户名）

        :return:
            username: 用户名 | null
        """
        username = request.user.username if request.user.username else None
        return JsonResponse({'username': username})

    @web_service()
    def post(request, data):
        """
        设置当前用户的用户名

        :param data:
            username: 匹配 [a-zA-Z0-9_]{4,20} 的字符串，且非纯数字
        :return: 200 | 400 | 403
        """
        if request.user.username:  # 用户名只能设置一次
            return HttpResponseForbidden()
        elif not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', data['username']) \
                or data['username'].isdigit():
            return HttpResponseBadRequest()
        else:
            try:
                request.user.username = data['username']
                request.user.save()
                return HttpResponse()
            except IntegrityError:
                return HttpResponseBadRequest()

    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return HttpResponseForbidden()


@web_service()
def user_password(request, data):
    """
    修改密码

    :param data:
        password: 密码，长度不小于6位
        old_password: 旧密码
    :return: 200 | 400 | 403
    """
    if len(data['password']) < 6:
        return HttpResponseBadRequest()

    if request.user.check_password(data['old_password']):
        request.user.set_password(data['password'])
        request.user.save()
        return HttpResponse()
    else:
        return HttpResponseForbidden()


def user_profile(request, user_id=None):
    @web_service(method='GET')
    def get(request, user_id):
        """
        获取用户个人资料

        :return:
            username: 用户名
            name: 昵称
            email: 邮箱地址
            description: 个人描述
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日（格式：YYYY-MM-DD）
            location: 位置信息（列表类型，格式：[x, y]，x：省索引，y：市索引）
            tags: 标签列表
            create_time: 注册时间
        """
        if not user_id:
            user = request.user
        else:
            try:
                user_id = int(user_id)
                user = User.enabled.get(id=user_id)
            except (User.DoesNotExist, KeyError):
                return HttpResponseBadRequest()

        if user is not request.user:  # 更新来访信息
            update_visitor(user, request.user)

        r = {  # from User
            'name': user.name,
            'username': user.username,
            'email': user.email,
            'create_time': user.create_time,
        }

        try:  # from UserProfile
            profile = user.profile
            r['description'] = profile.description
            r['gender'] = profile.gender
            r['birthday'] = profile.birthday.strftime('%Y-%m-%d') \
                if profile.birthday else None
        except UserProfile.DoesNotExist:
            r['description'] = ''
            r['gender'] = 0
            r['birthday'] = None

        # from UserLocation
        r['location'] = get_location(user)

        # from UserTag
        r['tags'] = get_tags(user)

        return JsonResponse(r)

    @web_service()
    @transaction.atomic
    def post(request, data):
        """
        修改用户个人资料

        :param data: 接受以下数据项
            name: 昵称
            description: 个人描述
            email: 邮箱地址
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日（格式：YYYY-MM-DD）
            location: 位置信息（列表类型）
                [x, y] | [x, None] | [None, None]
            tags: 标签列表
        :return: 200 | 400

        """
        user = request.user

        # to User
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        user.save()

        try:  # to UserProfile
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
        if 'description' in data:
            profile.description = data['description']
        if 'gender' in data:
            if data['gender'] not in [0, 1, 2]:
                return HttpResponseBadRequest()
            profile.gender = data['gender']
        if 'birthday' in data:
            if not data['birthday']:
                profile.birthday = None
            else:
                profile.birthday = datetime.strptime(
                    data['birthday'], '%Y-%m-%d').date()
        profile.save()

        # to UserLocation
        if 'location' in data:
            set_location(user, data['location'])

        # to UserTag
        if 'tags' in data:
            set_tags(user, data['tags'])

        return HttpResponse()

    if request.method == 'GET':
        return get(request, user_id)
    elif request.method == 'POST' and not user_id:
        return post(request)
    else:
        return HttpResponseForbidden()


def user_identification(request):
    @web_service(method='GET')
    def get(request):
        """
        获取当前用户的身份信息

        :return:
            name: 真实姓名
            number: 身份证号
            is_verified: 是否通过验证
        """
        try:
            r = {
                'name': request.user.identification.name,
                'number': request.user.identification.number,
                'is_verified': request.user.identification.is_verified,
            }
        except UserIdentification.DoesNotExist:
            r = {'name': '', 'number': '', 'is_verified': False}

        return JsonResponse(r)

    @web_service()
    def post(request, data):
        """
        修改当前用户的身份信息，若已通过身份认证则无法修改

        :param data:
            name: 真实姓名
            number: 身份证号
        :return: 200 | 400 | 403
        """
        identification, is_created = UserIdentification.objects.get_or_create(
            user=request.user)

        if not is_created and identification.is_verified:
            return HttpResponseForbidden()

        if 'name' in data:
            identification.name = data['name']
        if 'number' in data:
            if data['number'].isdigit() and len(data['number']) == 18:
                identification.number = data['number']
            else:
                return HttpResponseBadRequest()
        identification.save()

        return HttpResponse()

    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return HttpResponseForbidden()


@web_service(method='GET')
def user_identification_verification(request):
    """
    检查用户是否已经通过实名认证

    :return:
        is_verified: true | false
    """
    try:
        return JsonResponse(
            {'is_verified': request.user.identification.is_verified})
    except UserIdentification.DoesNotExist:
        return JsonResponse({'is_verified': False})


def user_student_identification(request, user_id=None):
    @web_service(method='GET')
    def get(request, user_id):
        """
        获取用户的学生信息

        :return:
            school: 学校名称
            number: 学生证号
        """
        if not user_id:
            user = request.user
        else:
            try:
                user_id = int(user_id)
                user = User.enabled.get(id=user_id)
            except (User.DoesNotExist, KeyError):
                return HttpResponseBadRequest()

        try:
            r = {
                'school': user.student_identification.school,
                'number': user.student_identification.number,
            }
        except UserStudentIdentification.DoesNotExist:
            r = {'school': '', 'number': ''}

        return JsonResponse(r)

    @web_service()
    def post(request, data):
        """
        设置当前用户的学生信息

        :param data:
            school: 学校名称
            number: 学生证号
        :return: 200 | 400
        """
        student_identification, is_created = \
            UserStudentIdentification.objects.get_or_create(user=request.user)

        if 'school' in data:
            student_identification.school = data['school']
        if 'number' in data:
            if data['number'].isdigit():
                student_identification.number = data['number']
            else:
                return HttpResponseBadRequest()
        student_identification.save()

        return HttpResponse()

    if request.method == 'GET':
        return get(request, user_id)
    elif request.method == 'POST' and not user_id:
        return post(request)
    else:
        return HttpResponseForbidden()
