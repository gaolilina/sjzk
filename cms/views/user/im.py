from django import forms

from im.huanxin import register_to_huanxin, update_password
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


class RegisterAllUserToHuanXin(BaseView):

    @cms_auth
    def post(self, request, **kwargs):
        qs = User.objects.all()
        for u in qs:
            code, desc = register_to_huanxin(u.phone_number, u.password, u.name)
            if code != 200:
                print('userid={} register error code={},desc={}'.format(u.id, code, desc))
        return self.success()


class UpdateAllUserPassword(BaseView):

    @cms_auth
    def post(self, request, **kwargs):
        qs = User.objects.all()
        for u in qs:
            code = update_password(u.phone_number, u.password)
            if code != 200:
                print('userid={} register error code={},desc={}'.format(u.id, code, 'user not found'))
        return self.success()
