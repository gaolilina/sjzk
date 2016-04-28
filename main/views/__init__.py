from datetime import datetime

from django.http import QueryDict
from django.views.generic import View

from main.models import User
from main.responses import *


class TokenRequiredView(View):
    """
    首先通过令牌检查用户身份，再指派具体方法处理请求

    """
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            token = request.GET.get('token')
        elif request.method == 'POST':
            token = request.POST.get('token')
        else:
            token = QueryDict(request.body).get('token')
        if not token:
            return Http401('token required')
        try:
            now = datetime.now()
            request.user = User.objects.get(
                token__value=token, token__expire_time__gte=now)
            if request.user.is_enabled:
                return super().dispatch(request, *args, **kwargs)
            else:
                return Http403('user is blocked')
        except User.DoesNotExist:
            return Http401('invalid or expired token')
