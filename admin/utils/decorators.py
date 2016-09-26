from functools import wraps

from main.utils import abort
from admin.models.admin_user import AdminUser


__all__ = ['require_cookie']


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

