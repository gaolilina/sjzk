from django import forms

from im.huanxin import register_to_huanxin
from main.models import User
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args


class RegisterToHuanXin(BaseView):

    @cms_auth
    @validate_args({
        'phone': forms.CharField(max_length=11, min_length=11),
    })
    def post(self, request, phone, **kwargs):
        qs = User.objects.filter(phone_number=phone)
        if not qs.exists():
            return self.fail(1, '用户不存在')
        u = qs.first()
        code, desc = register_to_huanxin(phone, u.password, u.name)
        if code != 200:
            return self.fail(2, desc)
        return self.success()
