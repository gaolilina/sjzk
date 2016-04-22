import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.http import QueryDict

from main.models.user import User
from main.responses import Http400, Http401, Http403


def require_token(function):
    """
    对被装饰的view函数进行用户身份验证

    :return: 401 | 403

    """
    def decorator(request, *args, **kwargs):
        if request.method == 'GET':
            token = request.GET.get('token')
        elif request.method == 'POST':
            token = request.POST.get('token')
        else:
            token = QueryDict(request.body).get('token')
        if not token:
            return Http401('token required')
        try:
            now = datetime.now()
            request.user = User.objects.get(
                token__value=token, token__expire_time__gte=now)
            if request.user.is_enabled:
                return function(request, *args, **kwargs)
            else:
                return Http403('user is blocked')
        except User.DoesNotExist:
            return Http401('invalid token')

    return decorator


def validate_input(d):
    """
    对被装饰的view函数利用字典进行输入数据验证
    验证后的数据分别作为关键字参数传入view函数中

    :param d: 值为 django.forms.Field 类型的字典
    :return: 400 | view函数的返回值

    """
    def decorator(function):
        def inner(request, *args, **kwargs):
            if request.method == 'GET':
                data = request.GET
            elif request.method == 'POST':
                data = request.POST
            else:
                data = QueryDict(request.body)
            for k, v in d.items():
                try:
                    kwargs[k] = v.clean(data[k])
                except KeyError:
                    if v.required:
                        return Http400('require argument "%s"' % k)
                except ValidationError:
                    return Http400('invalid argument "%s"' % k)
            return function(request, *args, **kwargs)

        return inner

    return decorator


def require_token_and_validate_input(d):
    """
    既验证用户身份，又验证输入数据

    :param d: 值为 django.forms.Field 类型的字典
    :return: 用于 django.utils.decorators.method_decorator 的装饰器列表

    """
    return [require_token, validate_input(d)]


def validate_json_input(d):
    """
    对被装饰的函数利用字典进行输入数据验证
    假设数据为JSON格式，保存于请求参数 data 中
    对 data 进行JSON解析并进行验证，验证后的数据作为关键字参数data传入view函数中

    :param d: 值为 django.forms.Field 类型的字典
    :return: 400 | view函数的返回值

    """
    def decorator(function):
        def inner(request, *args, **kwargs):
            try:
                if request.method == 'GET':
                    data = request.GET['data']
                elif request.method == 'POST':
                    data = request.POST['data']
                else:
                    data = QueryDict(request.body)['data']
            except KeyError:
                return Http400('require argument "data"')
            try:
                data = json.loads(data)
            except ValueError:
                return Http400('invalid argument "data"')
            for k, v in d.items():
                try:
                    data[k] = v.clean(data[k])
                except KeyError:
                    if v.required:
                        return Http400('require data "%s"' % k)
                except ValidationError:
                    return Http400('invalid data "%s"' % k)
            kwargs['data'] = data
            return function(request, *args, **kwargs)

        return inner

    return decorator


def require_token_and_validate_json_input(d):
    """
    既验证用户身份，又验证输入数据（JSON格式）

    :param d: 值为 django.forms.Field 类型的字典
    :return: 用于 django.utils.decorators.method_decorator 的装饰器列表

    """
    return [require_token, validate_json_input(d)]
