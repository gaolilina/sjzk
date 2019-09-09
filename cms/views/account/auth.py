from django import forms

from admin.models import AdminUser
from util.base.view import BaseView
from util.decorator.param import validate_args


class LoginByUsername(BaseView):

    @validate_args({
        'username': forms.CharField(max_length=20, required=False),
        'password': forms.CharField(min_length=6, max_length=32, strip=False),
    })
    def get(self, request, password, username=None):
        if username is None:
            return self.fail(3, '用户名不能为空')
        qs = AdminUser.enabled.filter(username=username)
        if not qs.exists():
            return self.fail(1, '用户不存在')
        user = qs.first()
        if user.password != password:
            return self.fail(2, '密码错误')
        return self.success({
            'token': user.token
        })
