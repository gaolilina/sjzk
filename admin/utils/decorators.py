from functools import wraps

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from main.utils import abort
from admin.models.admin_user import AdminUser
from admin.models.operation_log import OperationLog

__all__ = ['require_cookie', 'fetch_record', 'validate_args2']


def require_cookie(function):
    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        username = request.COOKIES.get('usr')
        password = request.COOKIES.get('pwd')
        if not username:
            return HttpResponseRedirect(reverse("admin:login"))
        try:
            user = AdminUser.objects.get(username=username)
            if user.is_enabled:
                if user.password[:6] == password:
                    request.user = user
                    return function(self, request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(reverse("admin:login"))
            return HttpResponseRedirect(reverse("admin:login"))
        except AdminUser.DoesNotExist:
            return HttpResponseRedirect(reverse("admin:login"))
    return decorator

def fetch_record(model, object_name, col):
    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            if col in kwargs:
                try:
                    v = kwargs.pop(col)
                    kw = {col: int(v) if col == 'id' else v}
                    obj = model.get(**kw)
                except ObjectDoesNotExist:
                    abort(404)
                else:
                    kwargs[object_name] = obj
            return function(*args, **kwargs)
        return inner
    return decorator

def validate_args2(d):
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
                        abort(400, 'require argument "%s"' % k)
                    if isinstance(v, forms.BooleanField):
                        kwargs[k] = False
                except ValidationError:
                    abort(400, 'invalid argument "%s"' % k)
            return function(self, request, *args, **kwargs)
        return inner
    return decorator

def admin_log(table, id, type, user):
    log = OperationLog(user=user, table=table, id=id, type=type)
    log.save()