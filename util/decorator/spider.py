from datetime import datetime
from functools import wraps

from django.http import JsonResponse

from modellib.models import ServerConfig
from modellib.models.ip_limit import IPLimit
from util.code.error import IP_LIMIT


def ip_limit(type):
    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            ip = request.META['HTTP_X_REAL_IP']
            data = IPLimit.objects.filter(ip=ip, type=type).first()
            # 未访问过，直接允许
            if data is None:
                IPLimit.objects.create(ip=ip, type=type)
                return function(self, request, *args, **kwargs)
            # 已锁定
            if data.is_lock:
                return error(data.code)

            now = datetime.now()
            duration = data.last_time - now

            config = ServerConfig.objects.first()
            update_data = {
                'last_time': now,
            }
            # 超速
            if duration < config.ip_limit_time:
                count = data.illegal_count + 1
                # 达到阈值,禁止访问
                if count >= config.ip_limit_count:
                    code = generate_code()
                    IPLimit.objects.filter(id=data.id).update(last_time=now, is_lock=True, code=code)
                    return error(code)
                # 未达到阈值
                update_data['illegal_count'] = count
                if count == 1:
                    update_data['first_time'] = now
            # 未超速时，需清除部分数据
            elif data.first_time is not None and (now - data.first_time) > config.ip_limit_time * config.ip_limit_count:
                update_data['first_time'] = None
                update_data['illegal_count'] = 0
            # 更新数据
            IPLimit.objects.filter(id=data.id).update(**update_data)
            # 有权限，允许访问
            return function(self, request, *args, **kwargs)

        return inner

    return decorator


def error(code):
    return JsonResponse({
        'code': IP_LIMIT,
        'msg': '访问过快，请验证',
        'data': code,
    })


def generate_code():
    return '1234'
