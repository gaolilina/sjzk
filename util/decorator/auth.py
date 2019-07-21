from functools import wraps

from django.http import JsonResponse

from admin.models import AdminUser


def cms_auth(function):
    """对被装饰的方法进行用户身份验证，并且当前用户模型存为request.user，
    用户令牌作为请求头X-User-Token进行传递
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token or AdminUser.objects.filter(token=token).count() <= 0:
            return JsonResponse({
                'code': -1
            })
        user = AdminUser.objects.get(token=token)
        if not user.is_enabled:
            return JsonResponse({
                'code': -4
            })
        # 用户正常
        request.user = user
        return function(self, request, *args, **kwargs)

    return decorator
