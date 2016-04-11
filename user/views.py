import re

from django.db import IntegrityError, transaction
from django.http import \
    JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from user.models import User, UserToken
from user.tools import decrypt_phone_info
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
