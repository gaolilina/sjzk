from functools import wraps

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from main.utils import abort
from admin.models.operation_log import OperationLog

__all__ = ['require_role', 'fetch_record', 'validate_args2', 'admin_log']


def require_role(role=None):
    """验证用户权限"""

    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            def check_role(source, target):
                for role in list(target):
                    if role in source:
                        return True
                return False

            if role is None:
                return function(self, request, *args, **kwargs)
            else:
                if check_role(request.user.role, role):
                    return function(self, request, *args, **kwargs)
                else:
                    return HttpResponseRedirect(reverse("admin:login"))

        return inner

    return decorator


def fetch_record(model, object_name, col):
    """根据url中的id抓取数据模型
    """

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
    同main.util.decorator.vlidate_args，针对checkbox提交有修正
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


def admin_log(table, id, type, user):
    """记录操作日志
    """
    log = OperationLog(user=user, table=table, data_id=id, operate_type=type)
    log.save()
