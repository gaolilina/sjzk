from django import forms
from django.views.generic import View

from main.models import UserValidationCode, User
from main.utils import abort
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class BindPhoneNumber(View):
    @app_auth
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, password, validation_code):
        """绑定手机号，若成功返回200
        param phone_number: 手机号
        :param password: 密码
        :param validation_code: 手机号收到的验证码

        :return 200
        """

        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400, '验证码与手机不匹配')

        if not request.user.check_password(password):
            abort(401, '密码错误')

        if User.enabled.filter(phone_number=phone_number).count() > 0:
            abort(404, '手机号已存在')

        request.user.phone_number = phone_number
        request.user.save()
        abort(200)