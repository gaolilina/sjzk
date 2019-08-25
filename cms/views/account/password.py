from django import forms

from main.models import UserValidationCode
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args
from util.message import send_message


class ChangePassword(BaseView):

    @cms_auth
    @validate_args({
        'phone': forms.CharField(max_length=11, min_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
    })
    def get(self, request, phone, password, **kwargs):
        """
        更换密码，需先验证原密码，在获取验证码，
        :param request:
        :param phone:
        :param password:
        :param kwargs:
        :return:
        """
        if not phone.isdigit():
            return self.fail(1, '手机号码格式不正确')
        user = request.user
        if user.phone_number and user.phone_number != phone:
            return self.fail(2, '您输入的手机号与当前用户手机号不符，请确认')
        if not user.check_password(password):
            return self.fail(3, '原密码错误')
        # 发送验证码
        code = UserValidationCode.generate(phone)
        tpl_value = "#code#=" + code
        send_message(phone, tpl_value)
        return self.success()

    @cms_auth
    @validate_args({
        'phone_number': forms.CharField(max_length=11, min_length=11),
        'validation_code': forms.CharField(min_length=6, max_length=6),
        'old_psd': forms.CharField(min_length=6, max_length=32),
        'password': forms.CharField(min_length=6, max_length=32),
    })
    def post(self, request, phone_number, old_psd, password, validation_code, **kwargs):
        """
        更换密码
        :param request:
        :param phone_number:
        :param old_psd:
        :param password:
        :param validation_code:
        :param kwargs:
        :return:
        """
        if not UserValidationCode.verify(phone_number, validation_code):
            return self.fail(1, '验证码错误')
        user = request.user
        if not user.check_password(old_psd):
            return self.fail(2, '原密码错误')
        user.set_password(password)
        user.save()
        user.update_token()
        return self.success()
