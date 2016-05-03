import json
from datetime import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import QueryDict

from main.models.user import User
from main.responses import *


def require_token(function):
    """
    对被装饰的方法进行用户身份验证

    :return: 401 | 403

    """
    def decorator(self, request, *args, **kwargs):
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
                return function(self, request, *args, **kwargs)
            else:
                return Http403('user is blocked')
        except User.DoesNotExist:
            return Http401('invalid token')
    return decorator


def validate_input(d):
    """
    对被装饰的方法利用字典进行输入数据验证
    验证后的数据分别作为关键字参数传入view函数中

    :param d: 值为 django.forms.Field 类型的字典
    :return: 400

    """
    def decorator(function):
        def inner(self, request, *args, **kwargs):
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
            return function(self, request, *args, **kwargs)
        return inner
    return decorator


def validate_json_input(d):
    """
    对被装饰的方法利用字典进行输入数据验证
    假设数据为JSON格式，保存于请求参数data中
    对data进行JSON解析并进行验证，验证后的数据作为关键字参数data传入view函数中

    :param d: 值为 django.forms.Field 类型的字典
    :return: 400

    """
    def decorator(function):
        def inner(self, request, *args, **kwargs):
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
            return function(self, request, *args, **kwargs)
        return inner
    return decorator


def check_object_id(model_manager, object_name):
    """
    检查某个ID对应的模型是否存在（若输入参数不存在则不处理）
    若不存在返回404 Not Found
    若存在则将输入参数中的ID转换成对应的模型实体传入view函数中

    :param model_manager: 模型的Manager
    :param object_name: 保存实体的参数名称，默认ID参数名称为 object_name + '_id'

    """
    def decorator(function):
        def inner(self, request, *args, **kwargs):
            id_name = object_name + '_id'
            if id_name in kwargs:
                _id = int(kwargs.pop(id_name))
                try:
                    _model = model_manager.get(id=_id)
                except ObjectDoesNotExist:
                    return Http404('object not exists')
                kwargs[object_name] = _model
            return function(self, request, *args, **kwargs)
        return inner
    return decorator
