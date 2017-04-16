from functools import wraps

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import QueryDict

from ..utils import abort
from ..models.user import User


__all__ = ['require_token', 'require_verification', 'validate_args',
           'fetch_object']


def require_token(function):
    """对被装饰的方法进行用户身份验证，并且当前用户模型存为request.user，
    用户令牌作为请求头X-User-Token进行传递
    """
    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token:
            abort(401)
        try:
            user = User.objects.get(token=token)
            if user.is_enabled:
                request.user = user
                return function(self, request, *args, **kwargs)
            abort(403)
        except User.DoesNotExist:
            abort(404)
    return decorator


def require_verification(function):
    """对被装饰的方法要求用户身份认证，该装饰器应放在require_token之后"""

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        if request.user.is_verified:
            return function(self, request, *args, **kwargs)
        abort(403)
    return decorator


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
                try:
                    kwargs[k] = v.clean(data[k])
                except KeyError:
                    if v.required:
                        abort(400, '需要参数 "%s"' % k)
                except ValidationError:
                    abort(400, '不合法参数 "%s"' % k)
            return function(self, request, *args, **kwargs)
        return inner
    return decorator


def fetch_object(model, object_name):
    """根据参数 "xxx_id" 在执行view函数前提前取出某个模型实例，
    作为参数 "xxx" 传入，若对象不存在则直接返回404 Not Found；
    若关键字参数中没有 "xxx_id" 则忽略
    """
    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            arg = object_name + '_id'
            if arg in kwargs:
                try:
                    obj_id = int(kwargs.pop(arg))
                    obj = model.get(id=obj_id)
                except ObjectDoesNotExist:
                    abort(404)
                else:
                    kwargs[object_name] = obj
            return function(*args, **kwargs)
        return inner
    return decorator
