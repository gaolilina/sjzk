from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from main.utils import abort
from admin.models.operation_log import OperationLog

__all__ = ['require_role', 'fetch_record', 'admin_log']


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
                    return HttpResponseRedirect('/login/')

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


def admin_log(table, id, type, user):
    """记录操作日志
    """
    log = OperationLog(user=user, table=table, data_id=id, operate_type=type)
    log.save()
