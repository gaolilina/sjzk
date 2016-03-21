import re

from django.db import IntegrityError, transaction
from django.http import \
    JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from user import decrypt_phone_info
from user.models import User, UserToken
from web_service.decorators import web_service


@web_service(require_token=False)
def token(request, data):
    """
    通过不同方式获取用户token

    :param data:
        method: 0 | 1 | 2
            0 - 通过手机号与IMEI信息获取token，需要参数 phone_info
            1 - 通过手机号与密码获取token，需要参数 phone_number / password
            2 - 通过用户名与密码获取token，需要参数 username / password
        phone_info: '加密' 后的手机号与IMEI信息，选填
        phone_number: 手机号，选填
        username: 用户名，选填
        password: 密码，选填
    :return:
        token: 用户token
    """

    def auto_register(phone_number, imei):
        with transaction.atomic():
            name = '新用户%s' % phone_number[-4:]
            user = User(phone_number=phone_number, imei=imei, name=name)
            user.save()
            token_info = UserToken(user=user)
            token_info.update()
        return user

    def get_by_phone_info(phone_info):
        try:  # '解密'
            phone_number, imei = decrypt_phone_info(phone_info)
        except ValueError:
            return HttpResponseForbidden()

        try:  # 检查数据库中是否存在相应的用户
            user = User.objects.get(phone_number=phone_number, imei=imei)
            if user.is_enabled:
                user.token_info.update()
                return JsonResponse({'token': user.token_info.token})
            else:
                return HttpResponseForbidden()
        except User.DoesNotExist:  # 若用户不存在则尝试注册一个新用户
            try:
                user = auto_register(phone_number, imei)
                return JsonResponse({'token': user.token_info.token})
            except IntegrityError:
                return HttpResponseForbidden()

    def get_by_phone_number(phone_number, password):
        try:
            user = User.objects.get(phone_number=phone_number)
            if user.check_password(password):
                user.token_info.update()
                return JsonResponse({'token': user.token_info.token})
            else:
                return HttpResponseForbidden()
        except User.DoesNotExist:
            return HttpResponseForbidden()

    def get_by_username(username, password):
        try:
            if not username:  # 用户可能设置了密码但没有设置用户名
                return HttpResponseForbidden()
            user = User.objects.get(username=username)
            if user.check_password(password):
                user.token_info.update()
                return JsonResponse({'token': user.token_info.token})
            else:
                return HttpResponseForbidden()
        except User.DoesNotExist:
            return HttpResponseForbidden()

    if data['method'] == 0:
        return get_by_phone_info(data['phone_info'])
    elif data['method'] == 1 and 'phone_number' in data and 'password' in data:
        return get_by_phone_number(data['phone_number'], data['password'])
    elif data['method'] == 2 and 'username' in data and 'password' in data:
        return get_by_username(data['username'], data['password'])
    else:
        raise Exception('invalid method code %s' % data['method'])


def username(request):
    @web_service(method='GET')
    def get(request):
        """
        获取当前用户的用户名

        :return:
            username - 用户名 | null
        """
        username = request.user.username if request.user.username else None
        return JsonResponse({'username': username})

    @web_service()
    def post(request, data):
        """
        设置当前用户的用户名

        :param data:
            username - 匹配 [a-zA-Z0-9_]{4,20} 的字符串
        :return: 200 | 400 | 403
        """
        if request.user.username:  # 用户名只能设置一次
            return HttpResponseForbidden()
        elif not re.fullmatch(r'[a-zA-Z0-9_]{4,20}', data['username']):
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
        return HttpResponseForbidden
