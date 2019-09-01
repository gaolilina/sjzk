from django import forms
from django.http import HttpResponseNotFound

from admin.models import AdminUser
from util.base.view import BaseView
from util.decorator.param import validate_args


class Login(BaseView):
    TYPE_PHONE = 'phone'
    TYPE_USERNAME = 'username'

    @validate_args({
        'method': forms.CharField(max_length=10),
        'username': forms.CharField(max_length=20, required=False),
        'phone': forms.CharField(max_length=11, min_length=11, required=False),
        'password': forms.CharField(min_length=6, max_length=32, strip=False),
    })
    def get(self, request, method, password, phone=None, username=None):
        if method == Login.TYPE_USERNAME:
            if username is None:
                return self.fail(3, '用户名不能为空')
            qs = AdminUser.enabled.filter(username=username)
        elif method == Login.TYPE_PHONE:
            if phone is None:
                return self.fail(4, '手机号不能为空')
            qs = AdminUser.enabled.filter(phone_number=phone)
        else:
            return HttpResponseNotFound()

        if not qs.exists():
            return self.fail(1, '用户不存在')
        user = qs.first()
        if user.password != password:
            return self.fail(2, '密码错误')
        return self.success({
            'token': user.token
        })
