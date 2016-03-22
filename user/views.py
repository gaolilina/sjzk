import re

from django.db import IntegrityError, transaction
from django.http import \
    JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from user import decrypt_phone_info
from user.models import User, UserToken
from web_service.decorators import web_service


@web_service(method='GET')
def user_root(request, data):
    """
    获取用户列表

    :param data:
        limit - 数量上限（默认值：10）
        offset - 偏移量（默认值：0）
        order - 排序方式
            0 - 注册时间降序（默认值）
            1 - 注册时间升序
            2 - 昵称升序
            3 - 昵称降序
    :return: JSON数组，每个元素包含以下属性
        id - 用户ID
        name - 用户昵称
        create_time - 注册时间
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


@web_service(method='GET')
def user_total(request):
    """
    获取用户总数

    :return:
        total - 用户总数
    """
    total = User.enabled.count()
    return JsonResponse({'total': total})


@web_service(require_token=False)
def user_token(request, data):
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


def user_username(request):
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


def user_password(request):
    @web_service(method='GET')
    def get(request):
        """
        用户是否已设置密码

        :return:
            has_password - true | false
        """
        has_password = True if request.user.password else False
        return JsonResponse({'has_password': has_password})

    @web_service()
    def post(request, data):
        """
        设置/修改密码

        :param data:
            password - 密码，长度不小于6位
            old_password - 旧密码，修改密码时
        :return: 200 | 400 | 403
        """
        if len(data['password']) < 6:
            return HttpResponseBadRequest()

        if not request.user.password or request.user.check_password(
                data['old_password']):
            request.user.set_password(data['password'])
            request.user.save()
            return HttpResponse()
        else:
            return HttpResponseForbidden()

    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return HttpResponseForbidden
