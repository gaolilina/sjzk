from django import forms
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..models import System as SystemModel, SystemNotification
from ..utils import abort
from ..utils.decorators import *


__all__ = ['VersionNumber', 'SystemNotificationList']


class VersionNumber(View):
    def get(self, request):
        """获取app当前版本号"""

        try:
            num = SystemModel.objects.get(id=1).VERSION_NUMBER
            return JsonResponse({'VERSION_NUMBER': num})
        except ObjectDoesNotExist:
            abort(400, '版本号不存在')

class SystemNotificationList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'history': forms.BooleanField(required=False),
    })
    def get(self, request, offset=0, limit=10, history=False):
        """获取系统通知"""

        if fetch_user_by_token(request) is False:
            history = True

        if history is False:
            r = SystemNotification.objects.filter(last__gt=request.user.system_notification_record.last)
            c = r.count()

            request.user.system_notification_record.last = c[0].id
            request.user.system_notification_record.save()
        else:
            r = SystemNotification.objects.all()
            c = r.count()
        records = (i for i in r[offset:offset + limit])
        l = [{'id': i.id,
              'content': i.content,
              'time_created': i.time_created,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})
