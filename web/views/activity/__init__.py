from functools import wraps

from django.http import JsonResponse


def activity_owner(activity_key='activity'):
    """
    活动权限
    """

    def inner(function):
        @wraps(function)
        def decorator(self, request, *args, **kwargs):
            if request.user != kwargs[activity_key].owner_user:
                return JsonResponse({
                    'code': 100,
                    'msg': '您不是活动的创办者',
                })

            return function(self, request, *args, **kwargs)

        return decorator

    return inner
