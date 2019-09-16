from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import User
from main.utils import abort
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class FindUserId(View):

    @app_auth
    @validate_args({
        'phone': forms.CharField(max_length=11, min_length=11),
    })
    def get(self, request, phone, **kwargs):
        qs = User.objects.filter(phone_number=phone)
        if not qs.exists():
            abort(404, '用户不存在')
        return JsonResponse({
            'id': qs.first().id
        })
