from functools import wraps

from main.models import User
from modellib.models.log import AppLog
from modellib.models.recommend.event import AppEvent


def app_log(event_name=None):
    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            response = function(self, request, *args, **kwargs)

            user = request.user if hasattr(request, 'user') else None

            # 记录日志
            log = AppLog()
            log.url = request.path_info
            log.user = user
            log.event = event_name
            log.ip = request.META['HTTP_X_REAL_IP']
            log.mac = request.META['HTTP_X_MAC']
            log.location = request.META['HTTP_X_LOCATION']
            log.manufacturers = request.META['HTTP_X_MANUFACTURERS']
            log.save()

            # 记录积分
            if event_name and user is not None:
                a = AppEvent.objects.filter(name=event_name).first()
                if a is not None and a.grade != 0:
                    User.objects.filter(id=user.id).update(score=user.score + a.grade)
            return response

        return inner

    return decorator
