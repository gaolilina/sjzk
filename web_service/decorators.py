import json

from ChuangYi import settings
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone

from user.models import User


def web_service(require_token=True, method='POST'):
    """
    对被装饰的view函数进行HTTP请求方式限制与用户token验证，
    验证失败则返回HTTP 403 Forbidden；
    若查询字符串中的包含参数data，将data作为JSON对象解析后填入view函数参数表中，
    若参数数量不匹配则返回HTTP 400 Bad Request

    :param require_token: 是否需要利用token验证用户身份
    :param method: 限定的HTTP请求方式，'POST' 或 'GET'

    """

    def decorator(view_function):
        def wrapped_view(request, *args, **kwargs):
            # 检查请求方式
            if request.method != method:
                return HttpResponseForbidden()

            # 利用token验证用户身份
            if require_token:
                # 将token从QueryDict中弹出，避免作为view函数的参数
                if method == 'POST':
                    token = request.POST.get('token')
                else:
                    token = request.GET.get('token')
                if not token:
                    return HttpResponseForbidden()

                try:
                    now = timezone.now()
                    user = User.enabled.get(
                        token_info__token=token,
                        token_info__expire_time__gte=now,
                    )

                    # 记录当前用户并更新用户最后一次活动时间
                    request.user = user
                    user.last_active_time = now
                    user.save()
                except User.DoesNotExist:
                    return HttpResponseForbidden()

            # 执行view函数，只在调试模式下抛出异常信息
            try:
                if method == 'POST':
                    data = request.POST.get('data')
                else:
                    data = request.GET.get('data')
                if data:
                    data = json.loads(data)
                    kwargs['data'] = data
                response = view_function(request, *args, **kwargs)
                return response
            except Exception as exception:
                if settings.DEBUG:
                    raise exception
                else:
                    return HttpResponseBadRequest()

        return wrapped_view

    return decorator
