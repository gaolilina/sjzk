from functools import wraps

from main.models import System
from main.models.role import Role
from ..models.user import User
from ..utils import abort

__all__ = ['require_token', 'require_role_token', 'require_verification_token', 'fetch_user_by_token']


def require_token(function):
    """对被装饰的方法进行用户身份验证，并且当前用户模型存为request.user，
    用户令牌作为请求头X-User-Token进行传递
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token:
            abort(401, '缺少参数token')
        try:
            user = User.objects.get(token=token)
            if user.is_enabled:
                request.user = user
                request.param = System.objects.get(
                    role__name=user.role if user.role else Role.objects.get(name__isnull=True).name)
                return function(self, request, *args, **kwargs)
            abort(403, '用户已删除')
        except User.DoesNotExist:
            abort(404, '用户不存在')

    return decorator


def require_verification_token(function):
    """对被装饰的方法进行用户实名验证，并且当前用户模型存为request.user，
    用户令牌作为请求头X-User-Token进行传递
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token:
            abort(401, '缺少参数token')
        try:
            user = User.objects.get(token=token)
            if user.is_enabled:
                if user.is_verified not in [2, 4]:
                    abort(403, '请先实名认证')
                request.user = user
                request.param = System.objects.get(
                    role__name=user.role if user.role else Role.objects.get(name__isnull=True).name)
                return function(self, request, *args, **kwargs)
            abort(403, '用户已删除')
        except User.DoesNotExist:
            abort(404, '用户不存在')

    return decorator


def require_role_token(function):
    """对被装饰的方法要求用户资格认证"""

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token:
            abort(401, '缺少参数token')
        try:
            user = User.objects.get(token=token)
            if user.is_enabled:
                if user.is_verified not in [2, 4]:
                    abort(403, '请先实名认证')
                elif user.is_role_verified != 2:
                    abort(403, '请先资格认证')
                request.user = user
                request.param = System.objects.get(
                    role__name=user.role if user.role else Role.objects.get(name__isnull=True).name)
                return function(self, request, *args, **kwargs)
            abort(403, '用户已删除')
        except User.DoesNotExist:
            abort(404, '用户不存在')

    return decorator


def fetch_user_by_token(request, force=False):
    token = request.META.get('HTTP_X_USER_TOKEN')
    if not token:
        if force:
            abort(401, '缺少参数token')
        return False
    try:
        user = User.objects.get(token=token)
        if user.is_enabled:
            request.user = user
            return True
        if force:
            abort(403, '用户已删除')
        return False
    except User.DoesNotExist:
        if force:
            abort(404, '用户不存在')
        return False
