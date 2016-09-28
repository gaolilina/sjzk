from functools import wraps

from django.core.exceptions import ObjectDoesNotExist

from main.utils import abort
from admin.models.admin_user import AdminUser


__all__ = ['require_cookie', 'fetch_record']


def require_cookie(function):
    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        username = request.COOKIES.get('usr')
        if not username:
            abort(401)
        try:
            user = AdminUser.objects.get(username=username)
            if user.is_enabled:
                request.user = user
                return function(self, request, *args, **kwargs)
            abort(403)
        except AdminUser.DoesNotExist:
            abort(401)
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
