from django.http import JsonResponse
from django.views.generic.base import View
from django.views.generic import View

class BaseView(View):

    def success(self, data=None):
        return JsonResponse({
            'code': 0,
            'data': data
        })

    def fail(self, code, msg=''):
        return JsonResponse({
            'code': code,
            'msg': msg
        })
