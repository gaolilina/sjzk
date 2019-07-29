'''
参数处理
'''
from functools import wraps

from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import QueryDict, JsonResponse

from main.utils import abort
from util.code import error


def validate_args(d):
    """对被装饰的方法利用 "参数名/表单模型" 字典进行输入数据验证，验证后的数据
    作为关键字参数传入view函数中，若部分数据非法则直接返回400 Bad Request
    """

    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            if request.method == 'GET':
                data = request.GET
            elif request.method == 'POST':
                data = request.POST
            else:
                data = QueryDict(request.body)
            for k, v in d.items():
                if k in kwargs:
                    request_value = kwargs.get(k)
                else:
                    request_value = data.get(k) or request.FILES.get(k)
                if request_value is None:
                    # 缺少必须参数
                    if v.required:
                        return JsonResponse({
                            'code': error.LACK_PARAM,
                            'msg': k
                        })
                    else:
                        continue
                try:
                    kwargs[k] = v.clean(request_value)
                except ValidationError:
                    # 参数值错误
                    return JsonResponse({
                        'code': error.INVALIDE_VALUE,
                        'msg': '不合法参数 {} 值 {}，正确类型为 {}'.format(k, request_value, type(v).__name__)
                    })
            return function(self, request, *args, **kwargs)

        return inner

    return decorator


def fetch_object(model, object_name, key_name=None, force=True):
    """
    根据请求中的参数，查出相应对象
    model：数据模型的 Manager
    object_name：对象名称，默认参数名为 object_name_id
    key_name：如果不是默认参数名，请使用这个参数
    force：是否强制，如果强制，出现错误时会报错，否则会忽略
    """

    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            arg = object_name + '_id' if key_name is None else key_name
            # 参数不存在，属于代码逻辑错误，直接抛异常
            if arg not in kwargs and force:
                raise Exception('{} not exist'.format(arg))

            if arg in kwargs:
                try:
                    obj_id = kwargs.pop(arg)
                    obj = model.get(id=obj_id)
                    kwargs[object_name] = obj
                except ObjectDoesNotExist:
                    if force:
                        return JsonResponse({
                            'code': error.OBJECT_NOT_FOUNT
                        })
            # else:
            # else 分支 force 一定为 FALSE，即忽略错误
            return function(*args, **kwargs)

        return inner

    return decorator


def old_validate_args(d):
    """
    这个装饰器不再维护，用于旧系统的验证参数用
    """

    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            if request.method == 'GET':
                data = request.GET
            elif request.method == 'POST':
                data = request.POST
            else:
                data = QueryDict(request.body)
            for k, v in d.items():
                try:
                    if data[k] != "":
                        kwargs[k] = v.clean(data[k])
                except KeyError:
                    if v.required:
                        abort(400, 'require argument "%s"' % k)
                    if isinstance(v, forms.BooleanField) and not isinstance(v, forms.NullBooleanField):
                        kwargs[k] = False
                except ValidationError:
                    abort(400, 'invalid argument "%s"' % k)
            return function(self, request, *args, **kwargs)

        return inner

    return decorator
